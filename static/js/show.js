// var sizes = [272,360,540,720,1080];
var sizes = [272,360];
var animation = true;

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
      video.addEventListener('play', fadeOutUIClutter, false)
      video.addEventListener('pause', fadeInUIClutter, false)
      video.addEventListener('ended', fadeInUIClutter, false)
    }
  }
  for(var i = 0; i< unlockButtons.length; i++){
    unlockButtons[i].addEventListener('click', unlockButtonClicked, true)
  }
  for(var i = 0; i< panelTabButtons.length; i++){
    panelTabButtons[i].addEventListener('click', panelTabClicked, true)
  }
  for(var i = 0; i< playButtons.length; i++){
    playButtons[i].addEventListener('click', playButtonClicked, true)
  }
}

function fadeOutUIClutter(e){
  var elements = $$('.box, .unlock-button, #header, #actions');
  for(var i=0; i< elements.length; i++){
    elements[i].addClass('lights-off')
  }
}
function fadeInUIClutter(e){
  var elements = $$('.box, .unlock-button, #header, #actions');
  for(var i=0; i< elements.length; i++){
    elements[i].removeClass('lights-off')
  }
}
function playButtonClicked(e){
  console.log('oi')
  videos = $$('.video')
  alert(videos[0].constructor)
  alert(videos[0].constructor == window.HTMLVideoElement)
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
      //video.erase('controls')
      if (box.hasClass('selected')){
        //var video_clone = video.clone()
        //video_clone.replaces(video)
        // video_clone.addEventListener('play', fadeOutUIClutter, false)
        // video_clone.addEventListener('pause', fadeInUIClutter, false)
        // video_clone.addEventListener('ended', fadeInUIClutter, false)
        video.addEventListener('play', fadeOutUIClutter, false)
        video.addEventListener('pause', fadeInUIClutter, false)
        video.addEventListener('ended', fadeInUIClutter, false)
      }
    }
    box.removeClass('selected')
    box.removeClass('below')
    downloadLink.removeClass('selected')
    // if(video.get('poster')){
    //   current_poster = video.get('poster')
    //   video.set('poster',current_poster.replace('-jpg-','-jpgbw-'))
    // }
    if (selected_size > size){
      box.addClass('below')
    } else if (selected_size == size){
      box.addClass('selected')
      downloadLink.addClass('selected')
      if (video){
        // if(video.get('poster')){
        //   current_poster = video.get('poster')
        //   video.set('poster',current_poster.replace('-jpgbw-','-jpg-'))
        // }
        video.set('controls', true)
        if (selected_size < 1080){
          // video.set('autobuffer', true)
        }
      }
    }
  }
  $('header').className = 'h'+selected_size;
  $('actions').className = 'a'+selected_size;
  $('play-button').className = 'p'+selected_size;
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
    if(animation){
      //retract any opening drawwer
      previousSelectedPanel.set('tween',{'duration':500,'transition':'quad:in'}).tween('top','-'+previousSelectedPanel.offsetHeight+'px');
      setTimeout(function(element){element.removeClass('opened')},500,previousSelectedPanel)
    } else{
      previousSelectedPanel.removeClass('opened')
    }
    previousSelectedTab[0].removeClass('selected')
  }
  if(closePanel) { return false }
  //resize panel container with height enough to fit the table
  selectedPanel.addClass('opened')
  panelContainer.style.height = Math.max(selectedPanel.offsetHeight,panelContainer.offsetHeight)
  if(animation){
    selectedPanel.style.top = '-'+selectedPanel.offsetHeight+'px'
    var openFx = new Fx.Tween(selectedPanel,{'duration':'normal','transition':'quad:out'}).start('top','0px');  
  }
  clickedTab.addClass('selected')
  return false;
}
