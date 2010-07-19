//For people without firebug
if (!console) {
  var console = {}
  console.log = function(text){
    return
  }
}


// var sizes = [272,360,540,720,1080];
var sizes = [272,360];

//init
$(document).ready(function(){
  initHacks();
  $('.play-button').click(playButtonClicked);
  //panel tab buttons
  $('#actions .menubar .tabs a').each(function(){
    $(this).click(panelTabClicked);
  });
  
  bindSizeBoxSelectionEvents();
});
function bindSizeBoxSelectionEvents(){
  $('.box').each(function(){
    $(this).bind({
      'click': boxClicked
      ,'mousedown': boxMouseDown
      ,'mouseup': boxMouseUp
      ,'mouseout': boxMouseUp
    });
  })
}
function unbindSizeBoxSelectionEvents(){
  $('.box').each(function(){
    $(this).unbind();
  });
}

function playButtonClicked(event){
  event.preventDefault();
  var video_container = $('.box.selected .video.container:last').get(0);
  //first run (if the proper src attributes are not yet in place)
  if (video_container.innerHTML.indexOf('src=""') != -1){
    //replace dummy video tag with the proper one (replace _src with src and replace the dom node)
    html = video_container.innerHTML.replace(/_src=\"h/g,'src="h').replace(/src=\"\"/g,'').replace('<video ','<video controls autoplay="true" ');
    video_container.innerHTML = html;
    //remove fake poster-frame
    $('.box.selected img.posterframe:last').fadeOut(1000);
  }else{
    $('.box.selected video:last').get(0).play();
  }
  //hide play button
  $('#main-play-button').fadeOut();
  //atach events to be triggered by the video playback
  fadeOutUIClutter();
  $('.box.selected video:last').bind('play', fadeOutUIClutter);
  $('.box.selected video:last').bind('pause ended', fadeInUIClutter);
}

function boxClicked(event){
  if ($(this).hasClass('selected') || $(this).hasClass('locked') || $(this).hasClass('lights-off')) return false;
  var box_id = $(this).attr('id')
  var selected_size = box_id.substring(1, box_id.length)
  for (var i=0; i<sizes.length; i++){
    var size = sizes[i];
    var box = $('#s' + size);
    var downloadLink = $('#d' + size);
    box.removeClass('selected below');
    downloadLink.removeClass('selected');
    if (selected_size > size){
      box.addClass('below')
    } else if (selected_size == size){
      box.addClass('selected')
      downloadLink.addClass('selected')
    }
  }
  $('#header').get(0).className = 'h'+selected_size;
  $('#actions').get(0).className = 'a'+selected_size;
  $('#main-play-button').get(0).className = 'p'+selected_size+' play-button';
  // displayPatron(selected_size);
  // updatePanelContainerHeight();
  event.stopPropagation();
}

function panelTabClicked(e){
  var clickedTab = $(this);
  var panelContainer = $('#panel-container')
  var selectedPanelID = clickedTab.attr('_panel');
  var selectedPanel = $('#' + selectedPanelID);
  var closePanel = clickedTab.hasClass('selected')
  var selectedTabs = $('#actions .menubar .tabs a.selected')
  e.stopPropagation();
  e.preventDefault();
  
  //the tab clicked is not currently selected
  if (!closePanel){
    //check if there is any previous opened panels to close
    if (selectedTabs.length > 0){
      //a different tab was selected
      previousSelectedTab = selectedTabs
      //close the opened panel
      var previousSelectedPanelID = previousSelectedTab.attr('_panel');
      var previousSelectedPanel = $('#' + previousSelectedPanelID)
      previousSelectedPanel.animate({
        'top': '-'+previousSelectedPanel.outerHeight()+'px'
      }, 1000, function(){
        $(this).removeClass('opened')
      });
      //remove the selected status on that tab
      previousSelectedTab.removeClass('selected')
      previousSelectedTab.attr('href', previousSelectedTab.attr('_panel_anchor'))
    }
    //open panel
    panelContainer.css('height', Math.max(selectedPanel.outerHeight(), panelContainer.outerHeight()))
    selectedPanel.addClass('opened')
    selectedPanel.css('top', -selectedPanel.outerHeight() + 'px')
    selectedPanel.animate({'top': '0px'}, 1000);
    clickedTab.addClass('selected')
  }else{
    //close panel
    selectedPanel.animate({
      'top': -selectedPanel.outerHeight() + 'px'
    }, 1000, function(){
      $(this).removeClass('opened')
    });
    clickedTab.removeClass('selected')
  }
  setTimeout(function(clickedTab){
    if (clickedTab.attr('href') == "#") { 
      clickedTab.attr('href', clickedTab.attr('_panel_anchor'))
    }else {
      clickedTab.attr('href','#')
    }
  }, 900, clickedTab)
}

function fadeOutUIClutter(){
  $('.box, .unlock-button, #header, #actions').each(function(){
    $(this).addClass('lights-off')
  });
  $('#main-play-button').fadeOut();
  //temporarily remove the box click handlers so the user can use the native play/pause controls
  unbindSizeBoxSelectionEvents();
}
function fadeInUIClutter(){
  $('.box, .unlock-button, #header, #actions').each(function(){
    $(this).removeClass('lights-off')
  });
  $('#main-play-button').fadeIn();
  bindSizeBoxSelectionEvents();
}
function boxMouseDown(event){}
function boxMouseUp(event){}

//--------------------Hacks-------------------------------------------------\\
function initHacks(){
  //hacks to make html5 video cross browser
  hack_addPosterFrameOverlay();
}

function hack_addPosterFrameOverlay(){
  //
  // Problem:
  // Firefox 3.5 does not support the video tag poster attribute.
  //
  // Solution:
  // Add the poster frame as an img tag with javascript an make it cover the 
  // other interface with css position absolute.
  $('video').each(function (){
    var video_height = $(this).attr('height')
    $('<img id="poster' + video_height
      + '" class="video posterframe" width="' + $(this).attr('width')
      + '" height="' + $(this).attr('height')
      + '" src="' + $(this).attr('poster')
      + '" />').insertAfter($(this))
  });
}