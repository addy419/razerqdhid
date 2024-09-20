import { ModelRef, ref, watch } from "vue";

export type BridgeData = {[key: string]: any};
export type BridgeStatus = {[key: string]: 'idle' | 'reading' | 'writing'};

export function makeBridge(bridgeData: ModelRef<BridgeData>, bridgeStatus: ModelRef<BridgeStatus>, props: any) {
  function bridge<T>(name: string, defaultValue: T, getPy: string, getLocals: () => object, setPy: string, setLocals: (value: Exclude<T, undefined>) => object) {
    bridgeData.value[name] ??= defaultValue;
    let modelRef = ref<T>(bridgeData.value[name]); // necessary as bridgeData of Array doesn't update when assigned with index
    let noWriteOnce = false;
    let noUpdateOnce = false;
    // the following watch is for updating self value when outer (upstream) value changes
    watch(() => bridgeData.value[name], (value) => {
      if (noUpdateOnce) { noUpdateOnce = true; return; }
      modelRef.value = value;
    }, {deep: true});
    // read is for fetching downstream value from the hardware
    const read = () => {
      if (props.hard) {
        bridgeStatus.value[name] = 'reading';
        props.py(getPy.replace('%p', 'profile=pt.Profile[profile]'), {
          locals: {profile: props.activeProfile.toUpperCase(), ...getLocals()}
        }).then((r: any) => {
          if (modelRef.value !== r) {
            noWriteOnce = true;
            modelRef.value = r;
          }
        }).finally(() => {
          bridgeStatus.value[name] = 'idle';
        });
      }
    };
    read();
    // if active profile changes, read
    watch(() => props.activeProfile, read);
    let lastWrite: number | null = null;
    // when self value changes, propagate to upstream and downstream
    watch(modelRef, (value) => {
      noUpdateOnce = true;
      bridgeData.value[name] = value; // sync outer value
      if (noWriteOnce) { noWriteOnce = false; return; }
      if (!props.hard || value === undefined) { return; }
      if (lastWrite) { clearTimeout(lastWrite); }
      bridgeStatus.value[name] = 'writing';
      lastWrite = setTimeout(() => { // rate limit the write operation
        lastWrite = null;
        props.py(setPy.replace('%p', 'profile=pt.Profile[profile]'), {
          locals: {profile: props.activeProfile.toUpperCase(), ...setLocals(value as Exclude<T, undefined>)}
        }).finally(() => {
          bridgeStatus.value[name] = 'idle';
        });
      }, 500);
    }, {deep: true});
    return modelRef;
  }
  return bridge;
}