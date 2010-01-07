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
      images[i].tween('opacity', 0.4)
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
  thumbs_available = images.length
  if (thumbs_available == 0) {return;} 
  gridbox = $('grid')
  w = gridbox.getWidth()
  h = window.getHeight()-160
  columns = Math.floor(w/193)
  rows = Math.floor(h/109)
  max_rows = Math.ceil((thumbs_available+1)/columns)
  max_grid_spots = max_rows *columns
  empty_cells = (max_grid_spots-(thumbs_available+1))
  grid_spots_per_screen = rows * columns
  // is_search_results = true
  if (is_search_results){
    left_align_last_row(empty_cells)
  }else{
    hide_extra_images(grid_spots_per_screen, thumbs_available, empty_cells, columns)
  }
}
//used to make the home page grid always a rectangle
function hide_extra_images(spots_available, thumbs_available, empty_cells, columns){
  if (spots_available < thumbs_available){
    last_img_cell = spots_available - 1
  } else {
    last_img_cell = thumbs_available - (columns-empty_cells)
  }
  for (i=0; i<images.length;i++){
    if(i < last_img_cell){
      images[i].parentNode.setStyle('display', 'inline-block')
    } else {
      images[i].parentNode.setStyle('display', 'none')
    }
  }
}
function left_align_last_row(empty_cells){
  placeholders = $$('span')
  if (placeholders.length == empty_cells) { return }
  //remove placeholders
  for (i=0; i<placeholders.length;i++){
    placeholders[i].dispose()
  }
  //add placeholders
  var placeholder = new Element('span',{'class':'grid_cell'})
  var grid_element = $('grid')
  for (i=0;i<empty_cells;i++){
    var new_placeholder = placeholder.clone()
    new_placeholder.inject(grid_element)  
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