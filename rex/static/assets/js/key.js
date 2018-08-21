$(function() {
	$('#key_quantity').on("change paste keyup", function() {
        var sva_usd = $('.sva_usd').val();
        console.log(sva_usd);
        var amount = $('#key_quantity').val();
        var amount_usd = parseFloat(amount)*12;
        var convert_usd_sva = (parseFloat(amount_usd) / parseFloat(sva_usd)).toFixed(8);
        $('#key_price').val(parseFloat(convert_usd_sva));
    });
})