require(['jquery','affix'],function(){
	$('.scroll-top').on('click',function(){
		var scrollTop = $(window).scrollTop();
		if (scrollTop >= 150){
			$('html,body').animate({scrollTop:0},'slow');
		}
	})
})