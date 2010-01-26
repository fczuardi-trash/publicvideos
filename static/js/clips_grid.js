var images
function submit_search(txt_input){
    document.location =  "/?q="+txt_input.value
}
function image_loaded(image_element){
  image_element.tween('opacity', [0, 1]);
}
function highlight_image(image_element){
  for (i=0; i<images.length;i++){
    if(images[i].id == 'corner_logo' || images[i].id == 'entry_logo') continue;
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
    if(images[i].id == 'corner_logo' || images[i].id == 'entry_logo') continue;
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
  setTimeout(remove_entry_logo,500)
}
function remove_entry_logo(){
  entry_logo = $('entry_logo')
  corner_logo = $('corner-form')
  entry_logo.set('tween', {duration: 'long'})
  corner_logo.set('tween', {duration: 'long'})
  entry_logo.tween('opacity', [1, 0]);
  corner_logo.tween('opacity', [0, 1]);
}
function window_resized(){
  thumbs_available = images.length
  if (thumbs_available == 0) {return;} 
  gridbox = $('grid')
  //temporarily remove scrollbar to get precise width
  document.body.setStyle('overflow','hidden')
  w = gridbox.getWidth()
  h = window.getHeight()-160
  columns = Math.floor(w/193)
  rows = Math.floor(h/109)
  max_rows = Math.ceil((thumbs_available)/columns)
  max_grid_spots = max_rows *columns
  empty_cells = (max_grid_spots-(thumbs_available))
  grid_spots_per_screen = rows * columns
  // is_search_results = true
  if (is_search_results){
    reposition_footer(columns, thumbs_available)
    if (thumbs_available > 1) {
      left_align_last_row(empty_cells)
    }
  }else{
    hide_extra_images(grid_spots_per_screen, thumbs_available, empty_cells, columns)
    reposition_footer(columns, thumbs_available)
  }
  //add back scrollbar if needed
  document.body.setStyle('overflow','auto')
}

function reposition_footer(columns, thumbs_available){
  footer = $('alpha-footer')
  gridbox = $('grid')
  footer.setStyle('top', gridbox.getHeight()+80+16)
  if (thumbs_available == 1){
    footer.setStyle('width', 192)
  } else {
    footer.setStyle('width', 192*columns+columns-2)
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
    if(images[i].id == 'corner_logo' || images[i].id == 'entry_logo') continue;
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
  var logo_cell = $('logo_108')
  for (i=0;i<empty_cells;i++){
    var new_placeholder = placeholder.clone()
    new_placeholder.inject(logo_cell,'before')  
  }
}
function init(){
  images = $$('img');
  for (i=0; i<images.length;i++){
    if(images[i].id == 'corner_logo'){continue;}
    images[i].set('opacity',0)
    images[i].addEvent('load', function(){image_loaded(this)});
    images[i].addEvent('mouseover', function(){highlight_image(this)});
  }
  $('grid').addEvent('mouseleave', highlight_all_images);
  $('logo_108').addEvent('mouseover', highlight_all_images);
  $('search').set('value',query_text);
  window.addEvent('load', page_loaded);
  window.addEvent('resize', window_resized);  
  window_resized();
}
init();