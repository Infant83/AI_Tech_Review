import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

const red = '#a50034';
const blue = '#6ca7c8';
const ink = '#30363d';
const muted = '#66717d';
const line = '#d9e0e6';

const nodes = [
  {id: 'CPU', sub: '제어와 분기', x: 735, y: 190, w: 130, h: 70},
  {id: 'GPU', sub: '대량 병렬', x: 250, y: 385, w: 150, h: 80},
  {id: 'TPU', sub: '행렬 데이터플로', x: 540, y: 385, w: 170, h: 80},
  {id: 'LPU', sub: '토큰 스트리밍', x: 840, y: 385, w: 170, h: 80},
  {id: 'NPU', sub: '엣지 추론', x: 1145, y: 385, w: 150, h: 80},
  {id: 'DPU', sub: '네트워크 오프로드', x: 465, y: 650, w: 185, h: 80},
  {id: 'QPU', sub: '양자 실험', x: 955, y: 650, w: 160, h: 80},
];

const flows = [
  {from: [800, 260], to: [325, 385], start: 0},
  {from: [800, 260], to: [625, 385], start: 10},
  {from: [800, 260], to: [925, 385], start: 20},
  {from: [800, 260], to: [1220, 385], start: 30},
  {from: [625, 465], to: [560, 650], start: 44},
  {from: [925, 465], to: [1035, 650], start: 58},
  {from: [560, 650], to: [1035, 650], start: 72},
];

const Chip = ({node}: {node: (typeof nodes)[number]}) => (
  <div
    style={{
      position: 'absolute',
      left: node.x,
      top: node.y,
      width: node.w,
      height: node.h,
      border: `2px solid ${ink}`,
      borderRadius: 8,
      background: '#fff',
      boxShadow: '0 16px 35px rgba(45, 55, 72, 0.12)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      gap: 4,
    }}
  >
    <div style={{fontSize: 30, color: ink, fontWeight: 800, letterSpacing: 0}}>{node.id}</div>
    <div style={{fontSize: 18, color: muted, letterSpacing: 0}}>{node.sub}</div>
    <div
      style={{
        position: 'absolute',
        bottom: -10,
        left: 22,
        right: 22,
        height: 10,
        borderRadius: 5,
        background: `linear-gradient(90deg, ${red}, #f2a2b7)`,
      }}
    />
  </div>
);

const Dot = ({from, to, start}: {from: number[]; to: number[]; start: number}) => {
  const frame = useCurrentFrame();
  const t = interpolate((frame - start + 150) % 90, [0, 90], [0, 1]);
  const x = from[0] + (to[0] - from[0]) * t;
  const y = from[1] + (to[1] - from[1]) * t;

  return (
    <div
      style={{
        position: 'absolute',
        left: x - 8,
        top: y - 8,
        width: 16,
        height: 16,
        borderRadius: 8,
        background: red,
        boxShadow: `0 0 18px ${red}`,
      }}
    />
  );
};

const flowPath = (from: number[], to: number[]) => {
  const midY = (from[1] + to[1]) / 2;
  return `M ${from[0]} ${from[1]} C ${from[0]} ${midY}, ${to[0]} ${midY}, ${to[0]} ${to[1]}`;
};

export const ProcessorRouting = () => {
  const frame = useCurrentFrame();
  const pulse = interpolate(frame % 45, [0, 22, 45], [0.25, 1, 0.25]);

  return (
    <AbsoluteFill style={{background: '#fbfcfd', fontFamily: 'Arial, sans-serif'}}>
      <svg width="1600" height="900" style={{position: 'absolute', inset: 0}}>
        <defs>
          <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill={blue} />
          </marker>
        </defs>
        <rect x="95" y="65" width="1410" height="770" rx="32" fill="#fff" stroke={line} />
        <text x="128" y="125" fill={ink} fontSize="36" fontWeight="800">
          이기종 AI 처리장치 라우팅
        </text>
        <text x="128" y="164" fill={muted} fontSize="20">
          같은 모델도 제어, 행렬 연산, 토큰 생성, 엣지 추론, 네트워크 처리가 서로 다른 병목을 갖습니다.
        </text>
        {flows.map((f, i) => (
          <path
            key={i}
            d={flowPath(f.from, f.to)}
            fill="none"
            stroke={blue}
            strokeWidth={6}
            strokeOpacity={0.38 + pulse * 0.2}
            markerEnd="url(#arrow)"
          />
        ))}
      </svg>
      {nodes.map((node) => (
        <Chip key={node.id} node={node} />
      ))}
      {flows.flatMap((flow, i) => [
        <Dot key={`${i}-a`} {...flow} />,
        <Dot key={`${i}-b`} {...flow} start={flow.start + 32} />,
      ])}
      <div
        style={{
          position: 'absolute',
          left: 128,
          bottom: 72,
          color: muted,
          fontSize: 20,
          letterSpacing: 0,
        }}
      >
        기준은 이름이 아니라 병렬성, 데이터 이동, 지연시간, 전력, 소프트웨어 스택입니다.
      </div>
    </AbsoluteFill>
  );
};
