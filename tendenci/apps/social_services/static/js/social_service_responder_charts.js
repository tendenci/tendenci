function responder_charts(e_skill, t_skill, med_skill, c_skill, ed_skill, mil_skill) {

  // Emergency Response Skills
  var e_legend = ['Paramedic','Fireman Trained','First Aid','Safety Manager','Police','Search and Rescue','Scuba Certified','Crowd Control']
  var e_data = []
  for (i=0; i<e_skill.length; i++) {
    e_data.push([e_legend[i], e_skill[i]])
  }
  var e_plot = jQuery.jqplot ('emergency-chart', [e_data], 
    { title: 'Emergency Response Skills',
      seriesDefaults: {
        renderer: jQuery.jqplot.PieRenderer, 
        rendererOptions: {
          fill: false,
          sliceMargin: 4,
          lineWidth: 5,
          showDataLabels: true
        }
      }, 
      legend: { show:true, location: 'e' }
    }
  );

  // Transportation Skills
  var t_legend = ['Paramedic','Fireman Trained','First Aid','Safety Manager','Police','Search and Rescue','Scuba Certified','Crowd Control']
  var t_data = []
  for (i=0; i<t_skill.length; i++) {
    t_data.push([t_legend[i], t_skill[i]])
  }
  var t_plot = jQuery.jqplot ('transpo-chart', [t_data], 
    { title: 'Transportation Skills',
      seriesDefaults: {
        renderer: jQuery.jqplot.PieRenderer, 
        rendererOptions: {
          fill: false,
          sliceMargin: 4,
          lineWidth: 5,
          showDataLabels: true
        }
      }, 
      legend: { show:true, location: 'e' }
    }
  );

  // Medical Skills
  var med_legend = ['Medical Doctor','Nurse']
  var med_data = []
  for (i=0; i<med_skill.length; i++) {
    med_data.push([med_legend[i], med_skill[i]])
  }
  var med_plot = jQuery.jqplot ('medical-chart', [med_data], 
    { title: 'Medical Skills',
      seriesDefaults: {
        renderer: jQuery.jqplot.PieRenderer, 
        rendererOptions: {
          fill: false,
          sliceMargin: 4,
          lineWidth: 5,
          showDataLabels: true
        }
      }, 
      legend: { show:true, location: 'e' }
    }
  );

  // Communication Skills
  var c_legend = ['Crisis Communications','Media','Author','Public Speaker','Politician','Blogger','Photographer','Videographer','Radio Operator','Actor','Thought Leader','Influencer']
  var c_data = []
  for (i=0; i<c_skill.length; i++) {
    c_data.push([c_legend[i], c_skill[i]])
  }
  var c_plot = jQuery.jqplot ('communication-chart', [c_data], 
    { title: 'Communication Skills',
      seriesDefaults: {
        renderer: jQuery.jqplot.PieRenderer, 
        rendererOptions: {
          fill: false,
          sliceMargin: 4,
          lineWidth: 5,
          showDataLabels: true
        }
      }, 
      legend: { show:true, location: 'e' }
    }
  );

  // Education Skills
  var ed_legend = ['Teacher','School Admin']
  var ed_data = []
  for (i=0; i<ed_skill.length; i++) {
    ed_data.push([ed_legend[i], ed_skill[i]])
  }
  var ed_plot = jQuery.jqplot ('education-chart', [ed_data], 
    { title: 'Education Skills',
      seriesDefaults: {
        renderer: jQuery.jqplot.PieRenderer, 
        rendererOptions: {
          fill: false,
          sliceMargin: 4,
          lineWidth: 5,
          showDataLabels: true
        }
      }, 
      legend: { show:true, location: 'e' }
    }
  );

  // Military Skills
  var mil_legend = ['Military Training','Desert Trained','Cold Weather Trained','Marksman']
  var mil_data = []
  for (i=0; i<mil_skill.length; i++) {
    mil_data.push([mil_legend[i], mil_skill[i]])
  }
  var mil_plot = jQuery.jqplot ('military-chart', [mil_data], 
    { title: 'Military Skills',
      seriesDefaults: {
        renderer: jQuery.jqplot.PieRenderer, 
        rendererOptions: {
          fill: false,
          sliceMargin: 4,
          lineWidth: 5,
          showDataLabels: true
        }
      }, 
      legend: { show:true, location: 'e' }
    }
  );
}
