# 2026-04-10 Encrypted LLM AI Data Protection Sources

## Topic
- Title: 동형암호 기반의 Encrypted LLM과 AI 데이터 보호
- Date package created: 2026-04-10
- Seed video URL: https://www.youtube.com/watch?v=j7QmCiowz7k
- Seed video channel: 국가인공지능전략위원회
- Seed video upload date: 2026-04-09
- Speaker: 서울대 수리과학부 천정희 교수
- Duration: 01:30:47

## Seed Materials In Workspace
- `sources/2026-04-09_동형암호 기반의 Encrypted LLM과 AI 데이터 보호 [j7QmCiowz7k].description`
- `sources/2026-04-09_동형암호 기반의 Encrypted LLM과 AI 데이터 보호 [j7QmCiowz7k].info.json`
- `sources/2026-04-09_동형암호 기반의 Encrypted LLM과 AI 데이터 보호 [j7QmCiowz7k].ko-orig.vtt`
- `sources/2026-04-09_동형암호 기반의 Encrypted LLM과 AI 데이터 보호 [j7QmCiowz7k].ko.vtt`
- `sources/2026-04-09_동형암호 기반의 Encrypted LLM과 AI 데이터 보호 [j7QmCiowz7k].ko-orig.clean.txt`

## Prompt Assets
- Prompt generator GPT share link: https://chatgpt.com/share/69d886fc-5ed4-83aa-b71c-8cd86948fbec
- Saved execution prompt: `notes/2026-04-10_encrypted-llm-ai-data-protection_deepresearch_prompt.md`

## Source Observations
- The seed video framing is about privacy-preserving AI using homomorphic encryption, with an explicit LLM angle.
- The likely analytical center is not just cryptography but the gap between cryptographic possibility and deployable enterprise inference.
- The talk appears positioned for a Korean public-sector or strategic AI security audience, so policy and regulated-industry implications matter.
- The clean transcript comes from YouTube auto-captions and should be treated as noisy source material rather than verbatim ground truth.

## Primary Research Directions
- Homomorphic encryption standards and benchmarking
- HE scheme trade-offs: CKKS, BFV/BGV, TFHE-family
- Encrypted transformer or LLM inference papers from 2024 to 2026
- Secure RAG and encrypted retrieval
- TEE and confidential computing alternatives for AI workloads
- Vendor and ecosystem landscape: CRYPTOLAB, OpenFHE, Microsoft, Azure confidential computing, Google confidential AI, Zama

## Primary Sources Collected
- Homomorphic Encryption Standard v1.1
  - https://homomorphicencryption.org/wp-content/uploads/2024/08/Homomorphic-Encryption-Standard-v1.1.pdf
- FHE Use-Cases and Benchmarking
  - https://homomorphicencryption.org/wp-content/uploads/2024/10/Benchmarking.pdf
- Open-Source Availability from HomomorphicEncryption.org
  - https://homomorphicencryption.org/availability/
- OpenFHE official site
  - https://openfhe.org/
- CODE.HEAAN official site
  - https://heaan.io/
- IBM Research on FHE and confidential computing
  - https://research.ibm.com/blog/fhe-cc-security
- IBM polynomial transformer paper for HE inference
  - https://research.ibm.com/publications/converting-transformers-to-polynomial-form-for-secure-inference-over-homomorphic-encryption
- AWS Nitro Enclaves overview
  - https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html
- AWS Nitro Enclaves attestation
  - https://docs.aws.amazon.com/enclaves/latest/user/set-up-attestation.html
- Azure confidential computing overview
  - https://learn.microsoft.com/en-us/azure/confidential-computing/overview
- Zama TFHE-rs overview
  - https://docs.zama.org/tfhe-rs/get-started/getting-started
- IBM AI on encrypted data via FHE
  - https://research.ibm.com/projects/ai-on-encrypted-data-via-fhe
- Powerformer ePrint
  - https://eprint.iacr.org/2024/1429
- AEGIS arXiv
  - https://arxiv.org/abs/2604.03425

## Validation Notes
- Seed video claims should be treated as hypotheses until matched against papers, official docs, standards, or official benchmark disclosures.
- Practicality claims need careful separation across demo, limited pilot, and production-adjacent stages.
