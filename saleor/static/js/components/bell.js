$('.fa-bell').on('click', (e) => {
	let $bell_class = $(e.target).attr('class');
	let $product_pk = $(e.target).attr('data-pk');
	let $url = $(e.target).attr('data-url');
  $.ajax({
      url: $url,
      method: 'post',
      headers: { 'products': $product_pk },
      data: {
        pk: $product_pk
      },
      success: () => {
        toggleBell(e);
      },
      error: (response) => {
        console.log(response);
      }
    });
});


export const hide_tooltips = () => {     
  $('[data-toggle="tooltip"]').tooltip('hide');
  // $('[data-toggle="tooltip-filter"]').tooltip('hide');
};

$('.fa-bell').hover(
       function(){ $(this).addClass('fa-lg') },
       function(){ $(this).removeClass('fa-lg') }
);

export const toggleBell = (e) => {
  let $bell_class = $(e.target).attr('class');
    if($bell_class.includes("far")){
    $(e.target).removeClass("far");
    $(e.target).addClass("fas");
  } else {
    $(e.target).removeClass("fas");
    $(e.target).addClass("far");
  }
};


export default $(document).ready((e) => {
  $('[data-toggle="tooltip"]').tooltip({placement: 'bottom',trigger: 'manual'}).tooltip('show');
  // $('[data-toggle="tooltip-filter"]').tooltip({placement: 'bottom',trigger: 'manual'}).tooltip('show');

  setTimeout(hide_tooltips, 10000)
});