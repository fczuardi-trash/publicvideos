var images
function submit_search(txt_input){
    document.location =  "/?q="+txt_input.value
}
function image_loaded(image_element){
  image_element.tween('opacity', [0, 1]);
}
function highlight_image(image_element){
  for (i=0; i<images.length;i++){
    images[i].set('tween', {duration: 'short'});
    if(images[i]==image_element){
      images[i].tween('opacity', 1)
    } else {
      images[i].tween('opacity', 0.3)
    }
  }
}
function highlight_all_images(){
  for (i=0; i<images.length;i++){
    images[i].set('tween', {duration: 'normal'});
    images[i].tween('opacity', 1)
  }
}
function page_loaded(){
  for (i=0; i<images.length;i++){
    if(images[i].get('opacity') == 0){
      image_loaded(images[i])
    }
  }
}
function window_resized(){
  gridbox = $('grid')
  w = gridbox.getWidth()
  h = window.getHeight()-130
  columns = Math.floor(w/193)
  rows = Math.floor(h/109)
  spots_available = rows * columns
  for (i=0; i<images.length;i++){
    if(i < spots_available-1){
      images[i].setStyle('display', 'block')
    } else {
      images[i].setStyle('display', 'none')
    }
  }
}
function init(){
  images = $$('img');
  for (i=0; i<images.length;i++){
    images[i].set('opacity',0)
    images[i].addEvent('load', function(){image_loaded(this)});
    images[i].addEvent('mouseover', function(){highlight_image(this)});
  }
  $('grid').addEvent('mouseleave', highlight_all_images);
  $('logo_108').addEvent('mouseover', highlight_all_images);
  window.addEvent('load', page_loaded);
  window.addEvent('resize', window_resized);  
  window_resized();
}
init();