$(function() {
    FnLending();
    FnLendingRe();
    function FnLending(){
        $('#verifyLending').click(function(){
            if($(this).is(':checked')){
                document.getElementById("btnLending").disabled = false;
            } else {
                document.getElementById("btnLending").disabled = true; 
            }
        });
        $('#verifyLending_t').click(function(){
            if($(this).is(':checked')){
                document.getElementById("btnLending_t").disabled = false;
            } else {
                document.getElementById("btnLending_t").disabled = true; 
            }
        });
        $('#btnLending').click(function(evt) {
        	swal({
                title: 'Are you sure?',
                text: '',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No',
                confirmButtonClass: "btn btn-success",
                cancelButtonClass: "btn btn-danger",
                buttonsStyling: false
            }).then(function() {
               $.ajax({
                    url: "/invest/LendingConfirm",
                    data: {
                        sva_amount: $('#sva_amount').val(),
                        usd_amount: $('#usd_amount').val(),
                        type_invest: $('#type_deposit').val()
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
                            $('.total_invest').html(data.new_total_invest),
                            $('#amount_sva').val(''),
                            $('#address_sva').val(''),
                            $('#password').val(''),
                            $('#Alert').show()
                        )
                    }
                });
              
            }, function(dismiss) {
              // dismiss can be 'overlay', 'cancel', 'close', 'esc', 'timer'
              if (dismiss === 'cancel') {
                swal({
                  title: 'Cancelled',
                  text: '',
                  type: 'error',
                  confirmButtonClass: "btn btn-info",
                  buttonsStyling: false
                }).catch(swal.noop);
              }
            })
        });


        $('#btnLending_t').click(function(evt) {
            swal({
                title: 'Are you sure?',
                text: '',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No',
                confirmButtonClass: "btn btn-success",
                cancelButtonClass: "btn btn-danger",
                buttonsStyling: false
            }).then(function() {
               $.ajax({
                    url: "/invest/InvestConfirm",
                    data: {
                        sva_amount: $('#sva_amount_t').val(),
                        usd_amount: $('#usd_amount_t').val(),
                        type_invest: $('#type_deposit_t').val()
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
                            $('.total_invest').html(data.new_total_invest),
                            $('#amount_sva').val(''),
                            $('#address_sva').val(''),
                            $('#password').val(''),
                            $('#Alert').show()
                        )
                    }
                });
              
            }, function(dismiss) {
              // dismiss can be 'overlay', 'cancel', 'close', 'esc', 'timer'
              if (dismiss === 'cancel') {
                swal({
                  title: 'Cancelled',
                  text: '',
                  type: 'error',
                  confirmButtonClass: "btn btn-info",
                  buttonsStyling: false
                }).catch(swal.noop);
              }
            })
        });

    }

    function FnLendingRe(){
        $('#verifyLendingre').click(function(){
            if($(this).is(':checked')){
                document.getElementById("btnLendingRe").disabled = false;
            } else {
                document.getElementById("btnLendingRe").disabled = true; 
            }
        });

        $('#btnLendingRe').click(function(evt) {
            swal({
                title: 'Are you sure?',
                text: '',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No',
                confirmButtonClass: "btn btn-success",
                cancelButtonClass: "btn btn-danger",
                buttonsStyling: false
            }).then(function() {
               $.ajax({
                    url: "/invest/LendingConfirmRe",
                    data: {
                        sva_amount: $('#sva_amount_reinvest').val(),
                        usd_amount: $('#usd_amount_reinvest').val()
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
                            $('.usd_balance').html(data.new_usd_balance),
                            $('.total_invest').html(data.new_total_invest),
                            $('#sva_amount_reinvest').val(''),
                            $('#usd_amount_reinvest').val(''),
                            $('#password').val(''),
                            $('#Alert').show()
                        )
                    }
                });
              
            }, function(dismiss) {
              // dismiss can be 'overlay', 'cancel', 'close', 'esc', 'timer'
              if (dismiss === 'cancel') {
                swal({
                  title: 'Cancelled',
                  text: '',
                  type: 'error',
                  confirmButtonClass: "btn btn-info",
                  buttonsStyling: false
                }).catch(swal.noop);
              }
            })
        });
    }


    $('#AllSVA').click(function(e){
        return false;
        var sva_balance = $(this).data("sva");
        var sva_usd = $('.sva_usd').val();
        var convert_usd_sva = (parseInt(sva_balance) * parseFloat(sva_usd)).toFixed(8)
        $('#usd_amount').val(parseFloat(convert_usd_sva));
        $('#sva_amount').val(parseFloat(sva_balance));
    });
    $('#Allusd_balance').click(function(e){
        var usd_balance = $(this).data("usd");
        var sva_usd = $('.sva_usd').val();
        $('#sva_amount_reinvest').val((parseInt(usd_balance)/parseFloat(sva_usd)).toFixed(8));
        $('#usd_amount_reinvest').val(parseInt(usd_balance));
    });

    $('#usd_amount_reinvest').on("change paste keyup", function() {
        var sva_usd = $('.sva_usd').val();
        var usd_balance = $('#usd_amount_reinvest').val();
        var convert_usd_sva = (parseFloat(usd_balance) / parseFloat(sva_usd)).toFixed(8);
        $('#sva_amount_reinvest').val(parseFloat(convert_usd_sva));
    });

    $('#usd_amount').on("change paste keyup", function() {
        var type = $('#type_deposit').val();
       
        var sva_usd = $('.sva_usd').val();
        var btc_usd = $('.btc_usd').val();
        // btc_usd = type == 'BTC' ? 1000 : 500;
        var usd_amount = $('#usd_amount').val();
        var amount_for_sva = parseFloat(usd_amount)/2;
        var convert_usd_btc = (parseFloat(amount_for_sva) / parseFloat(btc_usd)).toFixed(8);
        var convert_usd_sva = (parseFloat(amount_for_sva) / parseFloat(sva_usd)).toFixed(8);
        $('#sva_amount').val(parseFloat(convert_usd_sva));
        $('#btc_amount_invest').val(parseFloat(convert_usd_btc));
    });

    $('#usd_amount_t').on("change paste keyup", function() {
        var type = $('#type_deposit').val();
       
        var sva_usd = $('.sva_usd').val();
        var btc_usd = $('.btc_usd').val();
        // btc_usd = type == 'BTC' ? 1000 : 500;
        var usd_amount = $('#usd_amount_t').val();
        var amount_for_sva = parseFloat(usd_amount)/2;
        var convert_usd_btc = (parseFloat(amount_for_sva) / parseFloat(btc_usd)).toFixed(8);
        var convert_usd_sva = (parseFloat(amount_for_sva*0.6) / parseFloat(sva_usd)).toFixed(8);
        var convert_usdsva = (parseFloat(amount_for_sva*0.4)).toFixed(2);

        $('#usdsva_amount_t').val(parseFloat(convert_usdsva));

        $('#sva_amount_t').val(parseFloat(convert_usd_sva));
        $('#btc_amount_invest_t').val(parseFloat(convert_usd_btc));
    });



    $('#type_deposit').on("change paste keyup", function() {
        var type = $('#type_deposit').val();
        if (type == 'LTC') {
            $('#btc_amount_invest + span').html('LTC');
            $('#usd_amount').val(0);
            $('#btc_amount_invest').val(0);
            $('#sva_amount').val(0);
        }else{
            $('#btc_amount_invest + span').html('BTC');
            $('#usd_amount').val(0);
            $('#btc_amount_invest').val(0);
            $('#sva_amount').val(0);
        }
       
    });

$('#type_deposit_t').on("change paste keyup", function() {
        var type = $('#type_deposit_t').val();
        $('#usd_amount_t').val(0);
        $('#btc_amount_invest_t').val(0);
        $('#sva_amount_t').val(0);
        if (type == 'LTC') {
            $('#btc_amount_invest_t + span').html('LTC');
        }else{
            $('#btc_amount_invest_t + span').html('BTC');
        }
       
    });

    
    $('#btc_exchange_rate').on("change paste keyup", function() {     
        var sva_usd = $('.sva_usd').val();
        var btc_usd = $('.btc_usd').val();
        var ltc_usd = $('.ltc_usd').val();
        var btc_exchange_rate = $('#btc_exchange_rate').val();
        var usd_exchange_rate = (parseFloat(btc_usd) * parseFloat(btc_exchange_rate)).toFixed(2);
        $('#usd_exchange_rate').val(usd_exchange_rate);

        var ltc_exchange_rate = (parseFloat(usd_exchange_rate)/parseFloat(ltc_usd)).toFixed(8);
         $('#ltc_exchange_rate').val(ltc_exchange_rate);

        var sva_exchange_rate = (parseFloat(usd_exchange_rate)/parseFloat(sva_usd)).toFixed(8);

         $('#sva_exchange_rate').val(sva_exchange_rate);

    });
    $('#usd_exchange_rate').on("change paste keyup", function() {     
        var sva_usd = $('.sva_usd').val();
        var btc_usd = $('.btc_usd').val();
        var ltc_usd = $('.ltc_usd').val();
        var usd_exchange_rate = $('#usd_exchange_rate').val();

        var btc_exchange_rate = (parseFloat(usd_exchange_rate) / parseFloat(btc_usd)).toFixed(8);
        $('#btc_exchange_rate').val(btc_exchange_rate);
 
        var sva_exchange_rate = (parseFloat(usd_exchange_rate)/parseFloat(sva_usd)).toFixed(8);
         $('#sva_exchange_rate').val(sva_exchange_rate);

         var ltc_exchange_rate = (parseFloat(usd_exchange_rate)/parseFloat(ltc_usd)).toFixed(8);
         $('#ltc_exchange_rate').val(ltc_exchange_rate);

    });
    $('#sva_exchange_rate').on("change paste keyup", function() {     
        var sva_usd = $('.sva_usd').val();
        var btc_usd = $('.btc_usd').val();
        var ltc_usd = $('.ltc_usd').val();


        var sva_exchange_rate = $('#sva_exchange_rate').val();
        var sva_usd_exchange = parseFloat(sva_exchange_rate)*parseFloat(sva_usd);

        var btc_exchange_rate = (parseFloat(sva_usd_exchange) / parseFloat(btc_usd)).toFixed(8);
        $('#btc_exchange_rate').val(btc_exchange_rate);
       
         $('#usd_exchange_rate').val(sva_usd_exchange.toFixed(2));

         var ltc_exchange_rate = (parseFloat(sva_usd_exchange)/parseFloat(ltc_usd)).toFixed(8);
         $('#ltc_exchange_rate').val(ltc_exchange_rate);

    });
 $('#ltc_exchange_rate').on("change paste keyup", function() {     
        var sva_usd = $('.sva_usd').val();
        var btc_usd = $('.btc_usd').val();
        var ltc_usd = $('.ltc_usd').val();
        var ltc_exchange_rate = $('#ltc_exchange_rate').val();
        var usd_exchange_rate = (parseFloat(ltc_usd) * parseFloat(ltc_exchange_rate)).toFixed(2);
        $('#usd_exchange_rate').val(usd_exchange_rate);

        var btc_exchange_rate = (parseFloat(usd_exchange_rate)/parseFloat(btc_usd)).toFixed(8);
         $('#btc_exchange_rate').val(btc_exchange_rate);

        var sva_exchange_rate = (parseFloat(usd_exchange_rate)/parseFloat(sva_usd)).toFixed(8);

         $('#sva_exchange_rate').val(sva_exchange_rate);

    });
    // $('#sva_amount').on("change paste keyup", function() {
    //     var sva_usd = $('.sva_usd').val();
    //     var sva_amount = $('#sva_amount').val();
    //     var convert_usd_sva = (parseFloat(sva_amount) * parseFloat(sva_usd)).toFixed(8)
    //     $('#usd_amount').val(parseFloat(convert_usd_sva));
    // });

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