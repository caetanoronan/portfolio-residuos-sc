const COLORS = ["#66c2a5","#fc8d62","#8da0cb","#e78ac3","#a6d854","#ffd92f","#e5c494","#b3b3b3"];

const fmt = {
  int: v => (v ?? 0).toLocaleString('pt-BR'),
  ton: v => (v ?? 0).toLocaleString('pt-BR', {maximumFractionDigits: 2}),
  rate: v => `${v} kg/hab/dia`,
};

async function loadJSON(path){
  const r = await fetch(path);
  if(!r.ok) throw new Error(`Falha ao carregar ${path}`);
  return r.json();
}

async function main(){
  const [stats, munsResp, baciasResp] = await Promise.all([
    loadJSON('../api/v1/stats.json'),
    loadJSON('../api/v1/municipios.json'),
    loadJSON('../api/v1/bacias.json'),
  ]);

  // KPIs
  document.getElementById('kpi-municipios').textContent = fmt.int(stats.municipios);
  document.getElementById('kpi-populacao').textContent = fmt.int(stats.populacao);
  document.getElementById('kpi-residuos').textContent = fmt.ton(stats.residuos_totais_ton_ano);
  document.getElementById('kpi-taxa').textContent = fmt.rate(stats.residuos_per_capita_kg_dia);

  const municipios = munsResp.municipios || [];
  const bacias = baciasResp.bacias || [];

  // Gráfico: Resíduos por Bacia
  const x = bacias.map(b => b.bacia);
  const y = bacias.map(b => b.residuos_domestico_t_ano);
  const colors = x.map((_,i)=> COLORS[i % COLORS.length]);

  Plotly.newPlot('chart-bacias', [{
    type:'bar', x, y,
    marker: {color: colors},
    hovertemplate: '%{x}<br>%{y:.2f} t/ano<extra></extra>'
  }], {
    margin: {l:40,r:10,t:10,b:60},
    xaxis: {tickangle: -20},
    yaxis: {title: 't/ano'}
  }, {displayModeBar:false, responsive:true});

  // Gráfico: Top 10 Municípios
  const top = [...municipios]
    .sort((a,b)=> (b.residuos_domestico_t_ano||0) - (a.residuos_domestico_t_ano||0))
    .slice(0,10)
    .reverse(); // horizontal da base para o topo

  Plotly.newPlot('chart-top-mun', [{
    type:'bar',
    orientation:'h',
    x: top.map(m=> m.residuos_domestico_t_ano),
    y: top.map(m=> m.nome),
    marker:{color:'#1976d2'},
    hovertemplate: '%{y}<br>%{x:.2f} t/ano<extra></extra>'
  }], {
    margin: {l:120,r:10,t:10,b:40},
    xaxis: {title:'t/ano'}
  }, {displayModeBar:false, responsive:true});

  // Tabela (Tabulator)
  const table = new Tabulator('#tabela-municipios', {
    data: municipios,
    layout: 'fitColumns',
    height: 520,
    pagination: true,
    paginationSize: 15,
    columns: [
      {title:'Município', field:'nome', headerFilter:true},
      {title:'Bacia', field:'bacia'},
      {title:'População', field:'populacao', hozAlign:'right', formatter:(c)=> fmt.int(c.getValue())},
      {title:'Resíduos (t/ano)', field:'residuos_domestico_t_ano', hozAlign:'right', formatter:(c)=> fmt.ton(c.getValue())},
      {title:'Reciclável (t/ano)', field:'residuos_reciclavel_t_ano', hozAlign:'right', formatter:(c)=> fmt.ton(c.getValue())},
      {title:'Risco', field:'risco'},
    ]
  });

  // Busca global
  const input = document.getElementById('search');
  input.addEventListener('input', () => {
    const q = input.value?.toLowerCase() || '';
    if(!q){ table.clearFilter(true); return; }
    table.setFilter((row) => {
      const m = row.getData();
      return (m.nome||'').toLowerCase().includes(q) || (m.bacia||'').toLowerCase().includes(q);
    });
  });
}

main().catch(err => {
  console.error(err);
  alert('Falha ao carregar dados da API estática. Veja o console para detalhes.');
});
