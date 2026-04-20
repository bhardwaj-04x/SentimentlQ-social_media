'use strict';
document.addEventListener('DOMContentLoaded', () => {
  if (!trendData) return;

  const COLORS = { positive:'#10b981', negative:'#ef4444', neutral:'#06b6d4' };
  const grand  = trendData.grand;

  // India overall pie
  const pie = document.getElementById('india-pie');
  if (pie) {
    new Chart(pie, {
      type: 'doughnut',
      data: {
        labels: ['Positive','Negative','Neutral'],
        datasets: [{
          data: [grand.positive, grand.negative, grand.neutral],
          backgroundColor: ['#10b981','#ef4444','#06b6d4'],
          borderWidth: 0, hoverOffset: 8
        }]
      },
      options: {
        plugins: { legend: { position:'bottom', labels:{ padding:16, font:{size:12,weight:'600'} } } },
        cutout: '60%'
      }
    });
  }

  // Platform comparison grouped bar
  const bar = document.getElementById('platform-compare');
  if (bar) {
    new Chart(bar, {
      type: 'bar',
      data: {
        labels: trendData.labels,
        datasets: [
          { label:'Positive', data: trendData.positive, backgroundColor:'#10b981', borderRadius:6 },
          { label:'Negative', data: trendData.negative, backgroundColor:'#ef4444', borderRadius:6 },
          { label:'Neutral',  data: trendData.neutral,  backgroundColor:'#06b6d4', borderRadius:6 }
        ]
      },
      options: {
        responsive:true,
        plugins:{ legend:{ position:'top', labels:{ font:{size:11,weight:'600'} } } },
        scales:{
          x:{ grid:{display:false} },
          y:{ grid:{color:'#f1f5f9'}, ticks:{font:{size:11}}, beginAtZero:true }
        }
      }
    });
  }
});
