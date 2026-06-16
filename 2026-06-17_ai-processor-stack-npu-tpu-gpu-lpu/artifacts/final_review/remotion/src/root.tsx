import {Composition} from 'remotion';
import {ProcessorRouting} from './processor-routing';

export const Root = () => (
  <Composition
    id="ProcessorRouting"
    component={ProcessorRouting}
    durationInFrames={150}
    fps={30}
    width={1600}
    height={900}
  />
);
