//MooTools More, <http://mootools.net/more>. Copyright (c) 2006-2009 Aaron Newton <http://clientcide.com/>, Valerio Proietti <http://mad4milk.net> & the MooTools team <http://mootools.net/developers>, MIT Style License.

MooTools.More={version:"1.2.4.2",build:"bd5a93c0913cce25917c48cbdacde568e15e02ef"};Fx.Scroll=new Class({Extends:Fx,options:{offset:{x:0,y:0},wheelStops:true},initialize:function(b,a){this.element=this.subject=document.id(b);
this.parent(a);var d=this.cancel.bind(this,false);if($type(this.element)!="element"){this.element=document.id(this.element.getDocument().body);}var c=this.element;
if(this.options.wheelStops){this.addEvent("start",function(){c.addEvent("mousewheel",d);},true);this.addEvent("complete",function(){c.removeEvent("mousewheel",d);
},true);}},set:function(){var a=Array.flatten(arguments);if(Browser.Engine.gecko){a=[Math.round(a[0]),Math.round(a[1])];}this.element.scrollTo(a[0],a[1]);
},compute:function(c,b,a){return[0,1].map(function(d){return Fx.compute(c[d],b[d],a);});},start:function(c,g){if(!this.check(c,g)){return this;}var e=this.element.getScrollSize(),b=this.element.getScroll(),d={x:c,y:g};
for(var f in d){var a=e[f];if($chk(d[f])){d[f]=($type(d[f])=="number")?d[f]:a;}else{d[f]=b[f];}d[f]+=this.options.offset[f];}return this.parent([b.x,b.y],[d.x,d.y]);
},toTop:function(){return this.start(false,0);},toLeft:function(){return this.start(0,false);},toRight:function(){return this.start("right",false);},toBottom:function(){return this.start(false,"bottom");
},toElement:function(b){var a=document.id(b).getPosition(this.element);return this.start(a.x,a.y);},scrollIntoView:function(c,e,d){e=e?$splat(e):["x","y"];
var h={};c=document.id(c);var f=c.getPosition(this.element);var i=c.getSize();var g=this.element.getScroll();var a=this.element.getSize();var b={x:f.x+i.x,y:f.y+i.y};
["x","y"].each(function(j){if(e.contains(j)){if(b[j]>g[j]+a[j]){h[j]=b[j]-a[j];}if(f[j]<g[j]){h[j]=f[j];}}if(h[j]==null){h[j]=g[j];}if(d&&d[j]){h[j]=h[j]+d[j];
}},this);if(h.x!=g.x||h.y!=g.y){this.start(h.x,h.y);}return this;},scrollToCenter:function(c,e,d){e=e?$splat(e):["x","y"];c=$(c);var h={},f=c.getPosition(this.element),i=c.getSize(),g=this.element.getScroll(),a=this.element.getSize(),b={x:f.x+i.x,y:f.y+i.y};
["x","y"].each(function(j){if(e.contains(j)){h[j]=f[j]-(a[j]-i[j])/2;}if(h[j]==null){h[j]=g[j];}if(d&&d[j]){h[j]=h[j]+d[j];}},this);if(h.x!=g.x||h.y!=g.y){this.start(h.x,h.y);
}return this;}});