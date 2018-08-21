$(function() {
    
    FunctionAmountTransfer();
    FnSmTransfer();
    FunctionAmountTransferUSDCMS();
    FnSmTransferUSD();
    FnSmTransferSVAtoUSDSVA();
    function FunctionAmountTransfer() {
        $('#amount_transfer').on("change paste keyup", function() {
            var sva_usd = $('.sva_usd').val();
            var amount = $('#amount_transfer').val();

            if (isNaN(amount)) {
                $('#amount_transfer').val('0');
                $('#amount_transfer').val('0');
                $('#amount_transfer').addClass('error').attr('placeholder', 'Please enter is number!');
                return false;
            } else {
                $('#amount_transfer').removeClass('error').attr('placeholder', 'Amount');
            }
            if (parseFloat(amount) < 15) {
                $('#amount_transfer').addClass('error').attr('placeholder', 'Please enter amount > 15');
                return false;
            }
            var rate = (parseFloat(amount) / parseFloat(sva_usd)).toFixed(8);
            $('#amount_coin_transfer').val(parseFloat(rate));


        });
    }
    function FunctionAmountTransferUSDCMS() {
        $('#amount_transfer_usd').on("change paste keyup", function() {
            var sva_usd = $('.sva_usd').val();
            var btc_usd = $('.btc_usd').val();
            var amount = $('#amount_transfer_usd').val();



            if (isNaN(amount)) {
                $('#amount_transfer_usd').val('0');
                $('#amount_transfer_usd').val('0');
                $('#amount_transfer_usd').addClass('error').attr('placeholder', 'Please enter is number!');
                return false;
            } else {
                $('#amount_transfer_usd').removeClass('error').attr('placeholder', 'Amount');
            }
            if (parseFloat(amount) < 15) {
                $('#amount_transfer_usd').addClass('error').attr('placeholder', 'Please enter amount > 15');
                return false;
            }
            var amount_sva = parseFloat(amount)*0.2;
            var amount_btc = parseFloat(amount)*0.8;
            var rate_sva = (parseFloat(amount_sva) / parseFloat(sva_usd)).toFixed(8);
            $('#amount_coin_transfer_usd').val(parseFloat(rate_sva));
            var rate_btc = (parseFloat(amount_btc) / parseFloat(btc_usd)).toFixed(8);
            $('#amount_btc_transfer_usd').val(parseFloat(rate_btc));


        });
    }
    function FnSmTransferUSD() {
        $('#btn-transfer-usd').click(function(evt) {
            $.ajax({
                url: "/invest/transferusdcms",
                data: {
                    amount: $('#amount_transfer_usd').val()
                },
                type: "POST",
                beforeSend: function() {
                    $('.btnConfirm').button('loading');
                },
                error: function(data) {
                    $('.btnConfirm').button('reset');
                },
                success: function(data) {
                    $('.btnConfirm').button('reset');
                    var data = $.parseJSON(data);
                    data.status == 'error' ? (
                        showNotification('top', 'right', data.message, 'danger')
                    ) : (
                        showNotification('top', 'right', data.message, 'success'),
                        $('#amount_coin_transfer_usd').val('0'),
                        $('#amount_btc_transfer_usd').val('0'),
                        $('#amount_transfer_usd').val('0')
                    )
                }
            });
        });
    }
    function FnSmTransferSVAtoUSDSVA() {
        $('#svato_usdsva').on("change paste keyup", function() {
            var sva_usd = $('.sva_usd').val();
            var btc_usd = $('.btc_usd').val();
            var amount = $('#svato_usdsva').val();



            if (isNaN(amount)) {
                $('#svato_usdsva').val('0');
                $('#usdsva_amount').val('0');
                $('#svato_usdsva').addClass('error').attr('placeholder', 'Please enter is number!');
                return false;
            } else {
                $('#svato_usdsva').removeClass('error').attr('placeholder', 'Amount');
            }
            if (parseFloat(amount) < 5) {
                $('#svato_usdsva').addClass('error').attr('placeholder', 'Please enter amount > 5');
                return false;
            }
            var amount_usdsva = parseFloat(amount)*sva_usd;
       
          
            var rate_usdsva = (parseFloat(amount_usdsva)).toFixed(2);
            $('#usdsva_amount').val(parseFloat(rate_usdsva));


        });
        $('#btn-transferto-usdsva').click(function(evt) {
            $.ajax({
                url: "/invest/transferusdsva",
                data: {
                    amount: $('#svato_usdsva').val()
                },
                type: "POST",
                beforeSend: function() {
                    $('.btnConfirm').button('loading');
                },
                error: function(data) {
                    $('.btnConfirm').button('reset');
                },
                success: function(data) {
                    $('.btnConfirm').button('reset');
                    var data = $.parseJSON(data);
                    data.status == 'error' ? (
                        showNotification('top', 'right', data.message, 'danger')
                    ) : (
                        showNotification('top', 'right', data.message, 'success'),
                        $('#svato_usdsva').val('0'),
                        $('#usdsva_amount').val('0'),
                         setTimeout(function() {
                           location.reload()
                        }, 500)
                        
                       
                    )
                }
            });
        });
    }

    function FnSmTransfer() {
        $('#btn-transfer').click(function(evt) {
            $.ajax({
                url: "/invest/transferusd",
                data: {
                    amount: $('#amount_transfer').val()
                },
                type: "POST",
                beforeSend: function() {
                    $('.btnConfirm').button('loading');
                },
                error: function(data) {
                    $('.btnConfirm').button('reset');
                },
                success: function(data) {
                    $('.btnConfirm').button('reset');
                    var data = $.parseJSON(data);
                    data.status == 'error' ? (
                        showNotification('top', 'right', data.message, 'danger')
                    ) : (
                        showNotification('top', 'right', data.message, 'success'),
                        $('.sva_balance').html(data.new_sva_balance),
                        $('.usd_balance').html(data.new_usd_balance),
                        $('#amount_coin_transfer').val('0'),
                        $('#amount_transfer').val('0')
                    )
                }
            });
        });
    }


    function showNotification(from, align, msg, type) {
        /* type = ['','info','success','warning','danger','rose','primary'];*/
        var color = Math.floor((Math.random() * 6) + 1);
        $.notify({
            icon: "notifications",
            message: msg
        }, {
            type: type,
            timer: 3000,
            placement: {
                from: from,
                align: align
            }
        });
    }


})