import React, { useState } from 'react';
import html2canvas from 'html2canvas';

export default function App() {
  const [apiKey, setApiKey] = useState('');
  const [activeTab, setActiveTab] = useState<'scanner' | 'livescore'>('scanner');
  const [picks, setPicks] = useState<string[]>([
    "Tottenham",
    "AS Roma",
    "Middlesbrough",
    "Atl. Madrid"
  ]);
  const [analysisText, setAnalysisText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [images, setImages] = useState<File[]>([]);
  const [posterTitle, setPosterTitle] = useState<string>("Saturday Picks");

  // Kushughulikia picha zilizopakiwa
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setImages(Array.from(e.target.files));
    }
  };

  // Kufanya uchambuzi na Gemini AI
  const runAnalysis = async () => {
    if (!apiKey) {
      alert("Tafadhali weka Gemini API Key yako kwanza!");
      return;
    }
    if (images.length === 0) {
      alert("Tafadhali pakia screenshot ya mechi angalau moja!");
      return;
    }

    setLoading(true);
    try {
      // Badilisha picha kuwa Base64
      const imageParts = await Promise.all(
        images.map(async (file) => {
          return new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => {
              const base64data = (reader.result as string).split(',')[1];
              resolve(base64data);
            };
            reader.readAsDataURL(file);
          });
        })
      );

      // Wito wa Moja kwa Moja kwa Gemini API
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey.trim()}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  {
                    text: `Wewe ni Mkuu wa Kitengo cha Ujasusi wa Soka.
Kazi yako:
1. Tupa mechi zilizokwisha chezwa. Tumia mechi za leo/kesho ambazo HAZIJAANZA tu!
2. Teua mechi 4 tu salama kabisa (uhakika wa 90%+) zisizo na mitego.
3. Toa majibu kwa muundo huu kamili:

[PICKS]
★ Jina la Timu 1
★ Jina la Timu 2
★ Jina la Timu 3
★ Jina la Timu 4

[UCHAMBUZI]
Eleza kwa Kiswahili fasaha mbinu za makocha, fomu na kwanini mechi hizi 4 zimechaguliwa.`
                  },
                  ...imageParts.map((base64) => ({
                    inlineData: { mimeType: 'image/jpeg', data: base64 }
                  }))
                ]
              }
            ]
          })
        }
      );

      const data = await response.json();
      const rawText = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';

      if (rawText.includes('[PICKS]') && rawText.includes('[UCHAMBUZI]')) {
        const parts = rawText.split('[UCHAMBUZI]');
        const picksPart = parts[0].replace('[PICKS]', '').trim();
        const extractedPicks = picksPart
          .split('\n')
          .map((line: string) => line.replace('★', '').trim())
          .filter((line: string) => line.length > 0);

        if (extractedPicks.length > 0) {
          setPicks(extractedPicks.slice(0, 6));
        }
        setAnalysisText(parts[1].trim());
      } else {
        setAnalysisText(rawText);
      }
    } catch (err: any) {
      alert("Hitilafu: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Kupakua Bango kama Picha (PNG)
  const downloadPoster = () => {
    const element = document.getElementById('poster-canvas');
    if (!element) return;
    html2canvas(element, { scale: 2.5 }).then((canvas) => {
      const link = document.createElement('a');
      link.download = `${posterTitle.replace(/\s+/g, '_')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    });
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 p-4 md:p-8">
      {/* Header ya Kisasa */}
      <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center mb-8 border-b border-slate-800 pb-6 gap-4">
        <div>
          <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full text-xs font-black tracking-widest uppercase">
            ⚡ BETPRO REACT TERMINAL
          </span>
          <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-r from-emerald-400 via-teal-300 to-sky-400 bg-clip-text text-transparent mt-2">
            BetPro Tactical Syndicate
          </h1>
          <p className="text-slate-400 text-sm mt-1">Mfumo wa Kisasa wa Kijasusi wa Soka & Jenereta ya Mabango ya Mitandaoni</p>
        </div>

        {/* Tab Buttons */}
        <div className="flex bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('scanner')}
            className={`px-5 py-2.5 rounded-lg font-bold text-sm transition-all ${
              activeTab === 'scanner' ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20' : 'text-slate-400 hover:text-white'
            }`}
          >
            📸 Kichambuzi & Bango
          </button>
          <button
            onClick={() => setActiveTab('livescore')}
            className={`px-5 py-2.5 rounded-lg font-bold text-sm transition-all ${
              activeTab === 'livescore' ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20' : 'text-slate-400 hover:text-white'
            }`}
          >
            ⚽ LiveScores
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto">
        {activeTab === 'scanner' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* UPANDE WA KUSHOTO: Mipangilio & Kupakia */}
            <div className="lg:col-span-5 space-y-6">
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md">
                <h3 className="text-lg font-bold text-emerald-400 mb-4 flex items-center gap-2">
                  ⚙️ Usanidi wa Mechi
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5">Gemini API Key:</label>
                    <input
                      type="password"
                      placeholder="Weka API Key..."
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5">Kichwa cha Bango:</label>
                    <input
                      type="text"
                      value={posterTitle}
                      onChange={(e) => setPosterTitle(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5">Pakia Screenshot za Mechi:</label>
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageChange}
                      className="w-full text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20 cursor-pointer"
                    />
                  </div>

                  <button
                    onClick={runAnalysis}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black py-3 rounded-xl shadow-lg shadow-emerald-500/25 transition-all text-sm mt-2 disabled:opacity-50"
                  >
                    {loading ? "AI inachambua..." : "🚀 Fanya Uchambuzi & Unda Bango"}
                  </button>
                </div>
              </div>

              {/* Ripoti ya Kina */}
              {analysisText && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-xl">
                  <h4 className="text-sm font-bold text-sky-400 uppercase tracking-wider mb-2">📄 Ripoti ya Mbinu za Makocha:</h4>
                  <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{analysisText}</p>
                </div>
              )}
            </div>

            {/* UPANDE WA KULIA: BANGO LA KIJANI LENYE VIBAO VYEUPE */}
            <div className="lg:col-span-7 flex flex-col items-center">
              <div
                id="poster-canvas"
                className="w-full max-w-[460px] bg-[#00c82b] p-8 rounded-3xl shadow-2xl relative overflow-hidden text-center flex flex-col justify-between min-h-[580px]"
              >
                <div>
                  <h2 className="text-black font-black text-4xl tracking-tight mb-8 drop-shadow-sm">
                    {posterTitle}
                  </h2>

                  {/* Vibao Vyeupe vya Mlalo */}
                  <div className="space-y-4">
                    {picks.map((team, idx) => (
                      <div
                        key={idx}
                        className="bg-white text-black py-4 px-6 rounded-md shadow-md flex items-center font-extrabold text-2xl tracking-wide"
                      >
                        <span className="text-2xl mr-4 text-black">★</span>
                        <span>{team}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-8 text-black font-black text-xs tracking-widest uppercase opacity-90">
                  👑 BETPRO TACTICAL ANALYST
                </div>
              </div>

              {/* Kitufe cha Kupakua Bango */}
              <button
                onClick={downloadPoster}
                className="mt-6 flex items-center gap-2 bg-slate-900 hover:bg-slate-800 border-2 border-emerald-500 text-emerald-400 font-extrabold px-8 py-3.5 rounded-2xl shadow-xl transition-all"
              >
                📥 Pakua Picha ya Bango (PNG)
              </button>
            </div>
          </div>
        ) : (
          /* TAB YA LIVESCORE */
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            <iframe
              src="https://www.scorebat.com/embed/livescore/"
              className="w-full h-[800px] border-none"
              title="ScoreBat Live"
            />
          </div>
        )}
      </div>
    </div>
  );
}
