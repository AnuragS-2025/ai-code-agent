export default function Settings() {
  return (
    <div className="space-y-8">

      <h1 className="text-4xl font-bold">
        Settings
      </h1>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">

        <h2 className="text-2xl font-semibold mb-6">
          AI Configuration
        </h2>

        <div className="space-y-6">

          <div>
            <label className="block mb-2">
              AI Model
            </label>

            <select className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3">

              <option>Ollama</option>
              <option>OpenAI</option>
              <option>Gemini</option>

            </select>
          </div>

          <div>
            <label className="block mb-2">
              Default Scan Folder
            </label>

            <input
              placeholder="C:/Projects"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3"
            />
          </div>

          <div>
            <label className="block mb-2">
              API Key
            </label>

            <input
              type="password"
              placeholder="***************"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3"
            />
          </div>

          <button className="bg-cyan-500 hover:bg-cyan-600 px-6 py-3 rounded-lg font-semibold">
            Save Settings
          </button>

        </div>

      </div>

    </div>
  );
}