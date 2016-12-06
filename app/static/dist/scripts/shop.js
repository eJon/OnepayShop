require(["jquery","jquery-downcount","modal-box"],function(t){function n(){return t(".product-content").data("pid")}function e(){return t(".product-content").data("proid")}function i(t,n){return 0==t.children().length&&1==n?"load":t.children().length>=v&&t.children().length%v==0?"scroll":void 0}function o(n,e,i){t.get(n,function(n,o){if("success"==o&&"ok"==n.message)if(n.data&&n.data.length>0){var r=Handlebars.templates[i](n);if(e.append(r),n.data.length==v){var l;"join_tpl"==i?(u+=1,l=m):"show_tpl"==i&&(l=w,p+=1),a(l,e,i)}else t(".load-tips").fadeIn()}else t(".load-tips").fadeIn()})}function a(n,e,i){var a=t(window),r=t(document),l=0;d=function(){console.log(i);var t=window.innerHeight?window.innerHeight:a.height(),c=a.scrollTop()+t>r.height()-100,s=a.scrollTop()>l;if(c&&s&&(a.unbind("scroll",d),l=a.scrollTop(),n&&e&&i)){var h;"join_tpl"==i?h=n+"&page="+u:"show_tpl"==i&&(h=n+"&page="+p),o(h,e,i)}},a.bind("scroll",d)}function r(){return!!t("body").hasClass("login")}function l(){var n=Number(t('input[name="amount"]').val()),e=Number(t('input[name="pid"]').val()),i=Number(t(".join-select").find(".plus").data("max"));if("NaN"!=n.toString()&&"NaN"!=e.toString()&&0!=e&&"NaN"!=i.toString()){if(n>=1&&n<=i)return!0;t('input[name="amount"]').focus()}}var c=t(".down-count"),s=t(".diff-now");c.length>0&&c.downCount({finish:new Date(s.data("finish")).getTime(),now:1e3*parseFloat(s.data("now"))},function(){function t(){location.reload(),clearTimeout(timer_id)}c.find("span").text("0"),timer_id=setTimeout(t,4e3)}),Handlebars.registerHelper("compare",function(t,n,e){return t>n?e.fn(this):e.inverse(this)});var d,u=1,p=1,h=e(),f=n(),m="/api/v1.0/period_join_record?pid="+f,w="/api/v1.0/product_show?proid="+h,v=20;t(".tabs li").on("click",function(){function n(n){r.find("li").removeClass("current"),e.addClass("current");var i=t(".product-content");i.children().hide(),i.find(n).show(),d&&t(window).unbind("scroll",d)}var e=t(this),r=e.closest(".tabs"),l=r.find(".current");if(e.attr("class")!=l.attr("class"))if("tab-detail"==e.attr("class"))n(".product-detail");else if("tab-join"==e.attr("class")){n(".join-record");var c="join_tpl",s=t(".join-record"),h=i(s,u);"load"==h?o(m,s,c):"scroll"==h&&a(m,s,c)}else if("tab-show"==e.attr("class")){n(".product-show");var c="show_tpl",s=t(".product-show"),h=i(s,p);"load"==h?o(w,s,c):"scroll"==h&&a(w,s,c)}else n(".count-result")}),t(document).ready(function(){function n(n,i,o){var r="/api/v1.0/period_history?proid="+n+"&number="+i;o.prev(".loading-tips").show(),t.get(r,function(t,n){var i=Handlebars.templates.history_tpl(t);o.html(i),a=t.data.number,e(t.data.number),o.prev(".loading-tips").hide()})}function e(n){console.log(n,l);var e=t(".numbers-select").find(".left"),i=t(".numbers-select").find(".right");n==o?e.addClass("disabled"):e.removeClass("disabled"),n==l?i.addClass("disabled"):i.removeClass("disabled")}var i=t(".history-container"),o=Number(i.attr("no")),a=o,r=Number(i.data("status")),l=Number(i.attr("minno"));r||(o?n(h,o,i):i.html("<h3>开奖信息</h3><div>该商品暂无开奖信息</div>")),t(".period-nh").delegate(".history-period .left","click",function(){var e=t(this);e.hasClass("disabled")||a==o||n(h,a+1,i)}),t(".period-nh").delegate(".history-period .right","click",function(){var e=t(this);e.hasClass("disabled")||a==l||n(h,a-1,i)})}),t("body").delegate(".view-num","click",function(){var n=t("#num-modal"),e=t(this),i=e.data("num").toString();if(e.data("zj")){var o="<strong>"+e.data("zj")+"</strong>";i=i.replace(e.data("zj"),o)}n.find(".num-content").html(i),n.modal("show")}),t("form").find("button").on("click",function(){if(!r())return location.href="/login?next="+location.href,!1}),t('input[name="amount"]').on("keyup",function(){var n=t(this);1==n.val().length?n.val(n.val().replace(/[^1-9]/g,"1")):n.val(n.val().replace(/\D/g,"1"))}),t('input[name="amount"]').on("afterpaste",function(){var n=t(this);1==n.val().length?n.val(n.val().replace(/[^1-9]/g,"1")):n.val(n.val().replace(/\D/g,"1"))}),t(".join-select").find("a").on("click",function(){var n=t(this),e=1;if(n.hasClass("minus"))e=Number(n.next('input[name="amount"]').val()),"NaN"!=e.toString()&&e>1&&n.next('input[name="amount"]').val(e-1);else{e=Number(n.prev('input[name="amount"]').val());var i=Number(n.data("max"));"NaN"!=e.toString()&&e<i&&n.prev('input[name="amount"]').val(e+1)}}),t("button[type=submit]").on("click",function(){if(!l())return!1});var g=function(t){function n(t){return t=t.replace("{url}",e),t=t.replace("{title}",i),t=t.replace("{content}",o),t=t.replace("{pic}",a)}t=t||{};var e=t.url||window.location.href,i=t.title||document.title,o=t.content||"",a=t.pic||"";e=encodeURIComponent(e),i=encodeURIComponent(i),o=encodeURIComponent(o),a=encodeURIComponent(a);var r="http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url={url}&title={title}&pics={pic}&summary={content}",l="http://service.weibo.com/share/share.php?url={url}&title={title}&pic={pic}&searchPic=false",c="http://share.v.t.qq.com/index.php?c=share&a=index&url={url}&title={title}&appkey=801cf76d3cfc44ada52ec13114e84a96",s="http://widget.renren.com/dialog/share?resourceUrl={url}&srcUrl={url}&title={title}&description={content}",d="http://www.douban.com/share/service?href={url}&name={title}&text={content}&image={pic}",u="https://www.facebook.com/sharer/sharer.php?u={url}&t={title}&pic={pic}",p="https://twitter.com/intent/tweet?text={title}&url={url}",h="https://www.linkedin.com/shareArticle?title={title}&summary={content}&mini=true&url={url}&ro=true",f="http://qr.liantu.com/api.php?text={url}",m="http://connect.qq.com/widget/shareqq/index.html?url={url}&desc={title}&pics={pic}";this.qzone=function(){window.open(n(r))},this.weibo=function(){window.open(n(l))},this.tqq=function(){window.open(n(c))},this.renren=function(){window.open(n(s))},this.douban=function(){window.open(n(d))},this.facebook=function(){window.open(n(u))},this.twitter=function(){window.open(n(p))},this.linkedin=function(){window.open(n(h))},this.qq=function(){window.open(n(m))},this.weixin=function(t){t?t(n(f)):window.open(n(f))}};t(".shareto").find("a").on("click",function(){var n=t(this),e={title:t("title").text(),content:"1元就有机会购得"+t(".title").text(),pic:t(".product-img").find("img").attr("src")},i=new g(e);n.hasClass("share-to-weibo")?i.weibo():n.hasClass("share-to-qq")&&i.qzone()})});