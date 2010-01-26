// var sizes = [272,360,540,720,1080];
var sizes = [272,360];

function init(){
  var boxes = $$('.box');
  var unlockButtons = $$('.unlock-button')
  var panelTabButtons = $$('#actions .menubar .tabs a')
  var playButtons = $$('.play-button')
  for(var i = 0; i < boxes.length; i++){
    boxes[i].addEventListener('click', boxClicked, false)
    boxes[i].addEventListener('mousedown', boxMouseDown, false)
    boxes[i].addEventListener('mouseup', boxMouseUp, false)
    boxes[i].addEventListener('mouseout', boxMouseUp, false)
    boxes[i].addEventListener('rollout', boxMouseUp, false)
    var video = boxes[i].getLast('video')
    if(video){
      video.addEventListener('canplay', removeThrobber, false)
      video.addEventListener('play', fadeOutUIClutter, false)
      video.addEventListener('pause', fadeInUIClutter, false)
      video.addEventListener('ended', fadeInUIClutter, false)
    }
  }
  for(var i = 0; i< unlockButtons.length; i++){
    unlockButtons[i].addEventListener('click', unlockButtonClicked, true)
  }
  for(var i = 0; i< panelTabButtons.length; i++){
    panelTabButtons[i].addEventListener('click', panelTabClicked, false)
  }
  for(var i = 0; i< playButtons.length; i++){
    playButtons[i].addEventListener('click', playButtonClicked, true)
  }
  window.addEvent('load', page_loaded);
}
function page_loaded(){
  main_play_btn = $('main-play-button')
  main_play_btn.set('tween', {duration:'long'})
  main_play_btn.tween('opacity', [0,0.8])
}
function firefox35hack(video){
  var video_clone = video.clone()
  video_clone.replaces(video)
  video_clone.addEventListener('play', fadeOutUIClutter, false)
  video_clone.addEventListener('pause', fadeInUIClutter, false)
  video_clone.addEventListener('ended', fadeInUIClutter, false)
  video_clone.addEventListener('canplay', removeThrobber, false)
  video.dispose()
  return video_clone;
}
function removeThrobber(e){
  $('throbber').setStyle('display','none')
}
function fadeOutUIClutter(e){
  var elements = $$('.box, .unlock-button, #header, #actions');
  for(var i=0; i< elements.length; i++){
    elements[i].addClass('lights-off')
  }
  $('main-play-button').setStyle('display','none')
}
function fadeInUIClutter(e){
  var elements = $$('.box, .unlock-button, #header, #actions');
  for(var i=0; i< elements.length; i++){
    elements[i].removeClass('lights-off')
  }
  $('main-play-button').setStyle('display','block')
}
function playButtonClicked(e){
  var play_btn = $('main-play-button')
  var selected_size = play_btn.className.substring(1,play_btn.className.indexOf(' '))
  var box = $('s'+selected_size)
  var video = box.getLast('video')
  var video_sources = $$('#s'+selected_size+' video source')
  if(video.constructor == window.HTMLVideoElement){
    //browser has native support
    for (var i=0; i<video_sources.length;i++){
      video_sources[i].set('src', video_sources[i].get('_src'))
    }
    //check if it is Firefox 3.5.x because of a bug that does not refresh when you change attributes
    if ($('poster'+selected_size).getStyle('display') == 'block'){
      $('poster'+selected_size).setStyle('display','none')
      the_video =firefox35hack(video)
    } else{
      the_video = video;
    }
    the_video.setProperty('autobuffer','true')
    the_video.setProperty('autoplay','true')
    if (navigator.userAgent.indexOf('Gecko/') == -1){
      //firefox has a decent native throbber while safari and chrome don't give useful feedback
      $('throbber').setStyle('display','block')
    }
    the_video.play()
  }else{
    //fallback to flash player
    alert('Flash fallback not yet implemented, this is ALPHA')
  }
  //hide main play button
  $('main-play-button').setStyle('display','none')
}
function boxClicked(e){
  var target = (e.target.nodeName.toUpperCase() == 'DIV') ? e.target : e.target.parentNode;
  if (target.hasClass('selected') || target.hasClass('locked') || target.hasClass('lights-off')) return false;
  var selected_size = target.get('id').substring(1,target.get('id').length)
  for (var i=0; i<sizes.length;i++){
    var size = sizes[i];
    var box = $('s'+size)
    var downloadLink = $('d'+size)
    var video = box.getLast('video')
    if (video) {
      if (box.hasClass('selected')){
        video.addEventListener('play', fadeOutUIClutter, false)
        video.addEventListener('pause', fadeInUIClutter, false)
        video.addEventListener('ended', fadeInUIClutter, false)
      }
    }
    box.removeClass('selected')
    box.removeClass('below')
    downloadLink.removeClass('selected')
    if (selected_size > size){
      box.addClass('below')
    } else if (selected_size == size){
      box.addClass('selected')
      downloadLink.addClass('selected')
      if (video){
        video.set('controls', true)
        if (selected_size < 1080){
          // video.set('autobuffer', true)
        }
      }
    }
  }
  $('header').className = 'h'+selected_size;
  $('actions').className = 'a'+selected_size;
  $('main-play-button').className = 'p'+selected_size+' play-button';
  displayPatron(selected_size);
  updatePanelContainerHeight();
  e.stopPropagation();
  return false;
}
function updatePanelContainerHeight(){
  var panelContainer = $('panel-container')
  var selectedTab = $$('#actions .menubar .tabs a.selected')
  if (selectedTab[0]){
    var selectedPanel = $(selectedTab[0].get('_panel'))
    panelContainer.style.height = Math.max(selectedPanel.offsetHeight,panelContainer.offsetHeight)
  }
}
function unlockButtonClicked(e){
  e.stopPropagation();
  return false;
}
function displayPatron(size){
  var credit = $('unlocked-credit');
  var patrons = $$('#unlocked-credit span')
  var patron = $('patron'+size);
  if(patron){
    credit.style.display = 'inline';
    for (i=0; i< patrons.length; i++){
      patrons[i].style.display = 'none'
    }
    patron.style.display = 'inline'
  } else {
    if (credit) credit.style.display = 'none';
  }
}
function boxMouseDown(e){
  var target = (e.target.nodeName.toUpperCase() == 'DIV') ? e.target : e.target.parentNode;
  if ( target.hasClass('locked') && !target.hasClass('lights-off')){
    target.addClass('unauthorized')
    var selected_size = target.get('id').substring(1,target.get('id').length)
    $('b'+selected_size).addClass('highlight')
  }
}
function boxMouseUp(e){
  var target = (e.target.nodeName.toUpperCase() == 'DIV') ? e.target : e.target.parentNode;
  target.removeClass('unauthorized')
  var selected_size = target.get('id').substring(1,target.get('id').length)
  var lockbutton = $('b'+selected_size)
  if (lockbutton) lockbutton.removeClass('highlight')
}
function panelTabClicked(e){
  var clickedTab = e.target
  var panelTabButtons = $$('#actions .menubar .tabs a')
  var panelContainer = $('panel-container')
  var panels = $$('#panel-container .panel')
  var selectedPanel = $(clickedTab.get('_panel'))
  var previousSelectedTab = $$('#actions .menubar .tabs a.selected')
  var closePanel = clickedTab.hasClass('selected')
  e.stopPropagation();
  if (previousSelectedTab[0]){
    var previousSelectedPanel = $(previousSelectedTab[0].get('_panel'))
    //retract any opening drawwer
    if (previousSelectedTab.get('_panel_anchor') != clickedTab.get('_panel_anchor')) {
      previousSelectedTab.set('href',previousSelectedTab.get('_panel_anchor'))
    }
    //closing panel animation
    previousSelectedPanel.set('tween',{'duration':1000,'transition':'sine:in:out'}).tween('top','-'+previousSelectedPanel.offsetHeight+'px');
    setTimeout(function(previous_panel){
      previous_panel.removeClass('opened')
    },1500,previousSelectedPanel)
    previousSelectedTab[0].removeClass('selected')
  }
  if(!closePanel) { 
    //resize panel container with height enough to fit the table
    selectedPanel.addClass('opened')
    // selectedPanel.style.top = '-'+selectedPanel.offsetHeight+'px'
    selectedPanel.style.visibility = 'hidden'
    selectedPanel.style.top = '0px'
    panelContainer.setStyle('height',Math.max(selectedPanel.offsetHeight,panelContainer.offsetHeight))
    var openFx = new Fx.Tween(selectedPanel,{'duration':1000,'transition':'sine:in:out'}).start('top','-'+selectedPanel.offsetHeight+'px','0px');
    setTimeout(function(selectedPanel){
      selectedPanel.style.visibility = 'visible'
    },100,selectedPanel)
  } else {
    var scrollFx = new Fx.Scroll(window).toTop(window);
  }
  setTimeout(function(clickedTab){
    if (clickedTab.get('href') == "#") { 
      clickedTab.removeClass('selected')
      clickedTab.set('href',clickedTab.get('_panel_anchor'))
    }else {
      var anchorName = clickedTab.get('href')
      var anchor = $(anchorName.substring(1,anchorName.length))
      clickedTab.addClass('selected')
      var scrollFx = new Fx.Scroll(window, { offset: {
              'x': 0,
              'y': -50
          }
      }).toElement(anchor);
      clickedTab.set('href','#')
    }
  }, 900, clickedTab)
  
  return false;
}
