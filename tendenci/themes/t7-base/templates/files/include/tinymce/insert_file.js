$(document).on("click","button.insert-file",function(){
	var item_url = $(this).data("src");
	var item_alt = $(this).data("alt");

	//send image url back to TinyMce
    window.parent.postMessage({
        mceAction: 'customAction',
        src: item_url,
        alt: item_alt
    });
    //close external page and return to TinyMce
   // window.parent.postMessage({
   //     mceAction: 'close'
   // });
});
