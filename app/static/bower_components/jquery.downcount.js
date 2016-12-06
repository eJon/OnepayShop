(function ($) {
    $.fn.downCount = function (options, callback) {
        var settings = $.extend({
                finish: null,
                now:null
            }, options);
        var container = this;
        var finish = parseInt(settings.finish);
        console.log('finish:',finish);
        // 服务器端与客服端之间的时间差 这里的时间单位都是毫秒 经测试 fix不是一个固定值 会越來越大
        //这样一来 会导致客户端的diff比服务端的diff偏小
        var fix=new Date().getTime()-parseInt(settings.now);
        // var difference = parseInt(settings.difference);
        console.log(settings.now);
        console.log('fix:',fix);
        function countdown () {
            var difference=finish-(new Date().getTime()-fix);
            // difference = difference-40;
            if (difference < 0) {
                clearInterval(interval);
                if (callback && typeof callback === 'function') callback();
                return;
            }
            var hour = parseInt(difference / 1000 / 60 / 60 % 60),
            min = parseInt(difference / 1000 / 60 % 60),
            sec = parseInt(difference / 1000 % 60),
            mill = parseInt(difference % 1000);
            var html = '';
            var symbol = '<b>:</b>'
            if(hour>0){
                html = updateDuo(hour) + symbol + updateDuo(min) + symbol + updateDuo(sec) + symbol + updateDuo(mill);
            }else{
                html = updateDuo(min) + symbol + updateDuo(sec) + symbol + updateDuo(mill);
            }
            container.html(html);
        };
        function updateDuo(value){
            return '<span>'+Math.floor(value/10)%10+'</span><span>'+value%10+'</span>';
        }
        var interval = setInterval(countdown, 40);
    };
})(jQuery);