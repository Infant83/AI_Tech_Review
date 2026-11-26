"""Isolated FD primitive checks; no actual source, key or writer store."""
from pathlib import Path
import hashlib
import os
import stat
import tempfile
import unittest
from unittest.mock import patch

from scripts import admin_candidate_import as projection
from scripts import admin_projection_refs as refs
from scripts import admin_projection_jobs as writer


class RefPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(); self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        self.root = self.parent / "store"
        self.base, self.operation = "a" * 64, "b" * 64
        self.old, self.new, self.base_oid = "1" * 40, "2" * 40, "3" * 40
        self.base_path = "git/refs/adopt/bases/" + self.base
        self.ref_path = refs.DIRECTORY + "/" + self.operation
        self.pending_path = refs.DIRECTORY + "/.pending-" + self.operation
        with projection._Store(self.root, projection._Budget(), create=True) as store:
            store.write(".keep", b""); store.write("lock", b"")
            store.directory("git/refs/adopt/bases", create=True)
            store.directory(refs.DIRECTORY, create=True)
            store.write(self.base_path, (self.base_oid + "\n").encode())

    def snapshot(self, root=None):
        root = root or self.root
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*") if p.is_file() and not p.is_symlink()}

    def publish(self, expected=None, new=None, budget=None):
        with projection._Store(self.root, budget or projection._Budget()) as store, refs.locked_refs(store) as token:
            return refs.publish_ref(token, base_digest=self.base, base_oid=self.base_oid,
                operation=self.operation, expected_oid=expected, new_oid=new or self.new)

    def refuse(self, function, code):
        with self.assertRaises(refs.RefError) as error:
            function()
        self.assertEqual(error.exception.code, code)
        self.assertNotIn(str(self.parent), str(error.exception))

    def test_create_replace_exact_bytes_one_ref_no_subprocess(self):
        before = self.snapshot(); budget = projection._Budget()
        with patch("subprocess.Popen", side_effect=AssertionError("no child")):
            result = self.publish(budget=budget)
        self.assertEqual(result["refPayloadBytesWritten"], 41)
        self.assertFalse(result["nativeGitTransaction"])
        self.assertEqual(budget.write_bytes, 41)
        after = self.snapshot()
        self.assertEqual(set(after) - set(before), {self.ref_path})
        self.assertTrue(all(after[p] == value for p, value in before.items()))
        self.assertEqual(stat.S_IMODE((self.root / self.ref_path).stat().st_mode), 0o600)
        self.assertEqual(self.publish(expected=self.new, new=self.old)["after"], self.old)
        self.assertEqual((self.root / self.ref_path).read_bytes(), (self.old + "\n").encode())
        self.assertFalse((self.root / self.pending_path).exists())

    def test_bad_expected_or_base_refuses_before_temp(self):
        before = self.snapshot()
        self.refuse(lambda: self.publish(expected=self.old), "ref_conflict")
        self.assertEqual(before, self.snapshot())
        (self.root / self.base_path).write_bytes((self.old + "\n").encode())
        before = self.snapshot()
        self.refuse(self.publish, "store_inconsistent")
        self.assertEqual(before, self.snapshot())

    def test_lock_lifetime_pid_and_store_binding(self):
        self.refuse(lambda: refs.publish_ref(None, base_digest=self.base, base_oid=self.base_oid,
            operation=self.operation, expected_oid=None, new_oid=self.new), "writer_lock_required")
        with projection._Store(self.root, projection._Budget()) as store:
            with refs.locked_refs(store) as token:
                with patch.object(refs.os, "getpid", return_value=-1):
                    self.refuse(lambda: refs.publish_ref(token, base_digest=self.base, base_oid=self.base_oid,
                        operation=self.operation, expected_oid=None, new_oid=self.new), "writer_lock_required")
            self.refuse(lambda: refs.publish_ref(token, base_digest=self.base, base_oid=self.base_oid,
                operation=self.operation, expected_oid=None, new_oid=self.new), "writer_lock_required")

    def test_arguments_and_capability_fail_before_writes(self):
        before = self.snapshot()
        with projection._Store(self.root, projection._Budget()) as store, refs.locked_refs(store) as token:
            base = dict(base_digest=self.base, base_oid=self.base_oid, operation=self.operation,
                        expected_oid=None, new_oid=self.new)
            for field,value in [("operation","../escape"),("operation",True),("base_oid","0"*40),
                                ("new_oid","tag"),("expected_oid",0)]:
                with self.subTest(field=field,value=value):
                    self.refuse(lambda:refs.publish_ref(token, **{**base,field:value}),"invalid_ref_arguments")
            with patch.object(refs.os,"supports_dir_fd",set()):
                self.refuse(lambda:refs.publish_ref(token,**base),"unsupported_ref_platform")
        self.assertEqual(before,self.snapshot())

    def test_preexisting_pending_any_operation_preserved(self):
        pending = self.root / refs.DIRECTORY / (".pending-" + "c"*64)
        with projection._Store(self.root,projection._Budget()) as store:
            store.write(pending.relative_to(self.root).as_posix(),b"partial")
        before=self.snapshot();self.refuse(self.publish,"ref_incomplete")
        self.assertEqual(before,self.snapshot())

    def test_empty_pending_directory_other_operation_blocks_publish(self):
        with projection._Store(self.root,projection._Budget()) as store:
            store.directory(refs.DIRECTORY+"/.pending-"+"c"*64,create=True)
        before=self.snapshot();self.refuse(self.publish,"ref_incomplete")
        self.assertEqual(before,self.snapshot())
        self.assertFalse((self.root/self.ref_path).exists())

    def test_temp_fault_preserves_exact_partial_without_ref(self):
        original=os.write
        calls=0
        def short_then_fail(fd,raw):
            nonlocal calls
            calls+=1
            if calls==1:return original(fd,raw[:17])
            raise OSError("sensitive fixture detail")
        with patch.object(projection.os,"write",short_then_fail):
            self.refuse(self.publish,"ref_incomplete")
        self.assertEqual((self.root/self.pending_path).read_bytes(),(self.new+"\n").encode()[:17])
        self.assertFalse((self.root/self.ref_path).exists())
        before=self.snapshot();self.refuse(self.publish,"ref_incomplete");self.assertEqual(before,self.snapshot())

    def test_returned_short_write_counts_are_actual_not_full_buffer_charge(self):
        budget=projection._Budget();original=os.write;calls=0
        def short_then_fail(fd,raw):
            nonlocal calls
            calls+=1
            if calls==1:return original(fd,raw[:17])
            raise OSError("own fixture")
        with projection._Store(self.root,budget) as store, refs.locked_refs(store) as token:
            with patch.object(refs.os,"write",short_then_fail):
                self.refuse(lambda:refs.publish_ref(token,base_digest=self.base,base_oid=self.base_oid,
                    operation=self.operation,expected_oid=None,new_oid=self.new),"ref_incomplete")
            self.assertEqual(token.actual_ref_payload_bytes,17)
            self.assertEqual(budget.write_bytes,17)
        self.assertEqual((self.root/self.pending_path).stat().st_size,17)

    def test_actual_writer_budget_error_after_rename_becomes_unknown(self):
        budget=writer._Budget()
        def fault(stage):
            if stage=="after_rename":raise writer.JobError("job_timeout")
        with writer._Store(self.root,budget) as store, refs.locked_refs(store) as token:
            with patch.object(refs,"_checkpoint",fault):
                self.refuse(lambda:refs.publish_ref(token,base_digest=self.base,base_oid=self.base_oid,
                    operation=self.operation,expected_oid=None,new_oid=self.new),"outcome_unknown")
            self.assertEqual(token.actual_ref_payload_bytes,41)
        self.assertEqual((self.root/self.ref_path).read_bytes(),(self.new+"\n").encode())

    def test_actual_deadline_on_lock_exit_cannot_replace_unknown(self):
        for handled_inner in [False,True]:
            with self.subTest(handled_inner=handled_inner):
                if (self.root/self.ref_path).exists():(self.root/self.ref_path).unlink()
                budget=writer._Budget()
                def expire(stage):
                    if stage=="after_rename":budget.deadline=-1
                with self.assertRaises(refs.RefError) as error:
                    with writer._Store(self.root,budget) as store, refs.locked_refs(store) as token:
                        call=lambda:refs.publish_ref(token,base_digest=self.base,base_oid=self.base_oid,
                            operation=self.operation,expected_oid=None,new_oid=self.new)
                        if handled_inner:
                            with patch.object(refs,"_checkpoint",expire):self.refuse(call,"outcome_unknown")
                        else:
                            call();budget.deadline=-1
                self.assertEqual(error.exception.code,"outcome_unknown")
                self.assertFalse(token.active)
                self.assertEqual((self.root/self.ref_path).read_bytes(),(self.new+"\n").encode())

    def test_pre_rename_failure_preserves_temp_and_old(self):
        self.publish(new=self.old)
        def fault(stage):
            if stage=="before_rename":raise OSError("private fixture")
        with patch.object(refs,"_checkpoint",fault):
            self.refuse(lambda:self.publish(expected=self.old),"ref_incomplete")
        self.assertEqual((self.root/self.ref_path).read_bytes(),(self.old+"\n").encode())
        self.assertEqual((self.root/self.pending_path).read_bytes(),(self.new+"\n").encode())

    def test_rename_or_response_failure_is_unknown_and_not_rollback(self):
        for stage in ["after_rename","before_response"]:
            with self.subTest(stage=stage):
                if (self.root/self.ref_path).exists():(self.root/self.ref_path).unlink()
                def fault(current):
                    if current==stage:raise OSError("private")
                with patch.object(refs,"_checkpoint",fault):self.refuse(self.publish,"outcome_unknown")
                self.assertEqual((self.root/self.ref_path).read_bytes(),(self.new+"\n").encode())
                self.assertFalse((self.root/self.pending_path).exists())

    def test_root_or_nested_replacement_never_writes_canary(self):
        for target in ["root","nested"]:
            with self.subTest(target=target):
                if (self.root/self.ref_path).exists():(self.root/self.ref_path).unlink()
                directory=self.root if target=="root" else self.root/refs.DIRECTORY
                moved=directory.with_name(directory.name+"-moved")
                replacement=self.parent/("canary-"+target);replacement.mkdir(mode=0o700)
                (replacement/"sentinel").write_bytes(b"unchanged")
                before=self.snapshot(replacement)
                def fault(stage):
                    if stage=="before_rename":
                        directory.rename(moved);directory.symlink_to(replacement,target_is_directory=True)
                with patch.object(refs,"_checkpoint",fault):self.refuse(self.publish,"outcome_unknown")
                self.assertEqual(before,self.snapshot(replacement))
                actual=moved/self.ref_path if target=="root" else moved/self.operation
                self.assertEqual(actual.read_bytes(),(self.new+"\n").encode())
                directory.unlink();moved.rename(directory)

    def test_exact_write_limit_and_no_room_fail_before_temp(self):
        with patch.object(projection,"MAX_WRITE_BYTES",40):
            before=self.snapshot();self.refuse(self.publish,"import_limit");self.assertEqual(before,self.snapshot())
        with patch.object(projection,"MAX_WRITE_BYTES",41):self.publish()
        old=self.snapshot()
        with projection._Store(self.root,projection._Budget()) as store:
            store.scan();maximum=store.bytes
        with patch.object(projection,"MAX_STORE_BYTES",maximum):
            self.refuse(lambda:self.publish(expected=self.new,new=self.old),"store_limit")
        self.assertEqual(old,self.snapshot())

    def test_control_change_after_temp_refuses_before_publish(self):
        def fault(stage):
            if stage=="after_temp":(self.root/self.base_path).write_bytes((self.old+"\n").encode())
        with patch.object(refs,"_checkpoint",fault):self.refuse(self.publish,"ref_incomplete")
        self.assertFalse((self.root/self.ref_path).exists())
        self.assertTrue((self.root/self.pending_path).exists())

    def test_final_directory_fsync_failure_is_unknown(self):
        original=os.fsync
        def fault(fd):
            if (self.root/self.ref_path).exists():raise OSError("private")
            return original(fd)
        with patch.object(refs.os,"fsync",fault):self.refuse(self.publish,"outcome_unknown")
        self.assertEqual((self.root/self.ref_path).read_bytes(),(self.new+"\n").encode())


if __name__=="__main__":unittest.main()
