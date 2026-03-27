<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>CYBER-PATH | OPS CONSOLE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f1115; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .main-layout { display: grid; grid-template-columns: 1fr 480px; height: calc(100vh - 70px); }
        .content-scroll { overflow-y: auto; border-right: 1px solid #2d3748; }
        .details-panel { background: #16191e; overflow-y: auto; border-left: 1px solid #2d3748; }
        tr { border-bottom: 1px solid #1e293b; transition: background 0.2s; cursor: pointer; }
        tr:hover { background-color: #1a1d23; }
        tr.active { background-color: #2d3748; border-left: 4px solid #3b82f6; }
        .severity-high { color: #f87171; font-weight: 800; }
        .severity-med { color: #fbbf24; font-weight: 800; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
    </style>
</head>
<body class="h-screen flex flex-col overflow-hidden">

    <header class="h-[70px] bg-[#16191e] border-b border-[#2d3748] px-8 flex justify-between items-center shrink-0">
        <div class="flex items-center gap-8">
            <h1 class="text-lg font-bold tracking-tight text-white italic underline decoration-red-600 decoration-2">CYBER-PATH MONITORING</h1>
            <div class="flex gap-6 border-l border-slate-700 pl-8 font-mono text-sm">
                <div class="flex flex-col">
                    <span class="text-[10px] text-slate-500 uppercase font-bold">Local Time</span>
                    <span id="time-local" class="text-white">--:--:--</span>
                </div>
                <div class="flex flex-col border-l border-slate-800 pl-6">
                    <span class="text-[10px] text-slate-500 uppercase font-bold">UTC Time</span>
                    <span id="time-utc" class="text-slate-400">--:--:--</span>
                </div>
            </div>
        </div>
        <div class="text-xs font-bold uppercase text-green-500 flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div> Network Live
        </div>
    </header>

    <div class="main-layout">
        <section class="content-scroll">
            <table class="w-full text-left">
                <thead class="sticky top-0 bg-[#1a1d23] text-slate-500 text-[10px] uppercase tracking-widest border-b border-slate-800">
                    <tr>
                        <th class="p-4 text-center w-12"><i class="fa-solid fa-hashtag"></i></th>
                        <th class="p-4">Time</th>
                        <th class="p-4">Source</th>
                        <th class="p-4">Technique</th>
                        <th class="p-4 text-center">Risk</th>
                    </tr>
                </thead>
                <tbody id="alerts-body" class="text-sm"></tbody>
            </table>
        </section>

        <aside id="details-panel" class="details-panel p-8">
            <div id="panel-placeholder" class="h-full flex flex-col items-center justify-center text-slate-600 italic text-sm text-center">
                <i class="fa-solid fa-microscope text-4xl mb-4 opacity-20"></i>
                Sélectionnez une entrée pour analyser les données de mitigation
            </div>
            <div id="panel-content" class="hidden space-y-8"></div>
        </aside>
    </div>

    <script>
        let currentAlerts = [];
        let selectedId = null;

        function updateClocks() {
            const now = new Date();
            document.getElementById('time-local').innerText = now.toLocaleTimeString();
            document.getElementById('time-utc').innerText = now.toISOString().substr(11, 8);
        }

        async function fetchAlerts() {
            try {
                const response = await fetch('api.php');
                const data = await response.json();
                currentAlerts = data;
                renderTable();
                if (selectedId) updateDetails();
            } catch (err) { console.error("Data fetch error:", err); }
        }

        function renderTable() {
            const tbody = document.getElementById('alerts-body');
            tbody.innerHTML = '';
            currentAlerts.forEach(alert => {
                const isHighRisk = alert.risk_score > 0.7;
                const tr = document.createElement('tr');
                if (alert.id == selectedId) tr.className = 'active';
                tr.onclick = () => selectAlert(alert.id);
                tr.innerHTML = `
                    <td class="p-4 text-slate-600 font-mono text-xs text-center">${alert.id}</td>
                    <td class="p-4 text-slate-500 font-mono text-xs">${alert.timestamp.substr(11, 8)}</td>
                    <td class="p-4 font-bold text-slate-300">${alert.source_ip}</td>
                    <td class="p-4 text-slate-400 font-medium">${alert.tech_name}</td>
                    <td class="p-4 text-center ${isHighRisk ? 'severity-high' : 'severity-med'} text-xs">
                        ${(alert.risk_score * 100).toFixed(0)}%
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function selectAlert(id) {
            selectedId = id;
            renderTable();
            updateDetails();
        }

        function updateDetails() {
            const alert = currentAlerts.find(a => a.id == selectedId);
            if (!alert) return;

            document.getElementById('panel-placeholder').classList.add('hidden');
            const container = document.getElementById('panel-content');
            container.classList.remove('hidden');

            const mitreUrl = `https://attack.mitre.org/techniques/${alert.mitre_tid.split('.')[0]}`;
            
            // Formatage sécurisé des Data Sources
            const sources = (alert.data_sources || "Non spécifié").split(',').map(s => 
                `<span class="bg-slate-900 border border-slate-700 text-slate-400 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tighter">
                    <i class="fa-solid fa-database mr-1 opacity-50"></i>${s.trim()}
                </span>`
            ).join(' ');

            // Formatage des Mitigations (Parsing JSON)
            let mitigationsHtml = '<li class="text-xs text-slate-500 italic">Aucune donnée de mitigation</li>';
            if (alert.mitigations && alert.mitigations.startsWith('[')) {
                try {
                    const mitList = JSON.parse(alert.mitigations);
                    if (mitList.length > 0) {
                        mitigationsHtml = mitList.map(m => `
                            <li class="bg-black/20 p-3 rounded border border-blue-900/30">
                                <div class="flex justify-between items-start mb-1">
                                    <a href="${m.url}" target="_blank" class="text-blue-400 font-bold hover:underline text-xs flex items-center gap-1">
                                        <i class="fa-solid fa-shield-halved"></i> ${m.id} : ${m.name}
                                    </a>
                                    <span class="bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest cursor-help" title="Bloque ${m.protects_count} techniques d'attaque">
                                        Bloque ${m.protects_count} Tech.
                                    </span>
                                </div>
                            </li>
                        `).join('');
                    }
                } catch (e) {
                    console.error("Erreur parsing JSON mitigation", e);
                }
            }

            container.innerHTML = `
                <div class="border-b border-slate-800 pb-6">
                    <p class="text-[10px] text-blue-500 font-black uppercase tracking-widest mb-1">Incident Report</p>
                    <h2 class="text-2xl font-bold text-white leading-tight mb-4">${alert.tech_name}</h2>
                    <div class="flex flex-wrap gap-2">
                        <a href="${mitreUrl}" target="_blank" class="bg-blue-600/10 text-blue-400 border border-blue-500/30 px-3 py-1 rounded text-[10px] font-black hover:bg-blue-600 hover:text-white transition uppercase">
                            <i class="fa-solid fa-link mr-1"></i>MITRE ${alert.mitre_tid}
                        </a>
                        <span class="bg-slate-800 text-slate-400 px-3 py-1 rounded text-[10px] font-black uppercase italic tracking-tighter">${alert.tactic}</span>
                    </div>
                </div>

                <div class="space-y-6">
                    <div>
                        <p class="text-[10px] text-slate-500 uppercase font-black mb-3 tracking-widest">Stratégie de Défense (Mitigations)</p>
                        <ul class="space-y-2 bg-blue-900/5 p-4 rounded border border-blue-900/10">
                            ${mitigationsHtml}
                        </ul>
                    </div>

                    <div>
                        <p class="text-[10px] text-slate-500 uppercase font-black mb-3 tracking-widest">Origine des preuves (Data Sources)</p>
                        <div class="flex flex-wrap gap-2">${sources}</div>
                    </div>

                    <div class="grid grid-cols-2 gap-4 pt-2">
                        <div class="bg-black/40 p-3 rounded border border-slate-800">
                            <p class="text-[9px] text-slate-600 uppercase font-bold mb-1">Target</p>
                            <p class="text-xs text-slate-300 font-mono truncate">${alert.target_asset}</p>
                        </div>
                        <div class="bg-black/40 p-3 rounded border border-slate-800">
                            <p class="text-[9px] text-slate-600 uppercase font-bold mb-1">IP Source</p>
                            <p class="text-xs text-white font-mono font-bold">${alert.source_ip}</p>
                        </div>
                    </div>

                    <div>
                        <p class="text-[10px] text-slate-500 uppercase font-black mb-2">Trame Technique (Payload)</p>
                        <div class="bg-black p-4 rounded border border-slate-800 font-mono text-[11px] text-slate-400 break-all max-h-[150px] overflow-y-auto">
                            ${alert.raw_payload}
                        </div>
                    </div>
                </div>
            `;
        }

        setInterval(updateClocks, 1000);
        setInterval(fetchAlerts, 2000);
        updateClocks();
        fetchAlerts();
    </script>
</body>
</html>