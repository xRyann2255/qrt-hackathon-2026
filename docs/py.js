// Web Worker for Q5: load Pyodide from the CDN once, then cut, solve and score in Python (py/demo.py).
importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.5/full/pyodide.js');
const ready = (async () => {
  const py = await loadPyodide();
  for (const f of ['solver.py', 'generator.py', 'demo.py'])
    py.FS.writeFile(f, await (await fetch('py/' + f)).text());
  py.runPython('import sys; sys.path.insert(0, "."); import demo');
  return py.runPython('demo.run');
})();
onmessage = async ({data: {text, seed, extras}}) => {
  try {
    postMessage(JSON.parse((await ready)(text, seed, extras)));
  } catch (e) { postMessage({error: String(e)}); }
};
