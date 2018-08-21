"use strict";

$().ready(function(){
    $('#verify').click(function(){
            if($(this).is(':checked')){
                document.getElementById("submitRegister").disabled = false;
            } else {
                document.getElementById("submitRegister").disabled = true; 
            }
        });
});


$('#submitLogin').click(function(){
    $('form#frmLogin').submit();
    $('#submitLogin').hide();
})
$('#submitRegister').click(function(){
    $('form#frmRegister').submit();
    $('#submitRegister').hide();
})
$('#submitReset').click(function(){
    $('form#frmReset').submit();
    $('#submitReset').hide();
})