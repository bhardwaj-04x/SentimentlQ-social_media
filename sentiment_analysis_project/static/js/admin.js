'use strict';
// Admin dashboard charts
document.addEventListener('DOMContentLoaded', () => {
  // Pie chart — overall sentiment
  const pie = document.getElementById('admin-pie');
  if (pie && adminStats) {
    new Chart(pie, {
      type: 'doughnut',
      data: {
        labels: ['Positive','Negative','Neutral'],
        datasets: [{
          data: [adminStats.positive, adminStats.negative, adminStats.neutral],
          backgroundColor: ['#10b981','#ef4444','#06b6d4'],
          borderWidth: 0, hoverOffset: 8
        }]
      },
      options: {
        plugins: { legend: { position:'bottom', labels:{ padding:16, font:{size:12,weight:'600'} } } },
        cutout: '65%'
      }
    });
  }

  // Bar chart — platform breakdown
  const bar = document.getElementById('platform-bar');
  if (bar && platStats && platStats.length) {
    new Chart(bar, {
      type: 'bar',
      data: {
        labels: platStats.map(p => p.platform),
        datasets: [
          { label:'Positive', data: platStats.map(p=>p.pos||0), backgroundColor:'#10b981', borderRadius:6 },
          { label:'Negative', data: platStats.map(p=>p.neg||0), backgroundColor:'#ef4444', borderRadius:6 },
          { label:'Neutral',  data: platStats.map(p=>p.neu||0), backgroundColor:'#06b6d4', borderRadius:6 }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position:'top', labels:{ font:{size:11,weight:'600'} } } },
        scales: {
          x: { grid:{display:false}, stacked:false },
          y: { grid:{color:'#f1f5f9'}, ticks:{font:{size:11}} }
        }
      }
    });
  }
});
