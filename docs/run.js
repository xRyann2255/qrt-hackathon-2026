// Web Worker: run one compiled solver's main() on the given stdin and return its stdout.
onmessage = ({data: {q, input, env}}) => {
  importScripts(`wasm/${q}.js`);
  const bytes = new TextEncoder().encode(input), out = [];
  let i = 0, t0;
  solver({
    locateFile: f => 'wasm/' + f,
    stdin: () => i < bytes.length ? bytes[i++] : null,
    print: line => out.push(line),
    printErr: () => {},
    preRun: [m => { Object.assign(m.ENV, env); t0 = performance.now(); }],
    postRun: [() => postMessage({out: out.join('\n'), ms: performance.now() - t0})],
    onAbort: why => postMessage({error: String(why)}),
  });
};
