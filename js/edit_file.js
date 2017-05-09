window.onload = function init(){
    $('input[type=checkbox]').removeAttr('checked');
    $('[name="start"]').removeAttr('disabled');
    $('#psw1').removeClass('sgreen').addClass('sred');

    lines_option();
}

function check_button_start(){
    $('[name="start"]').removeAttr('disabled');

    $('select').each(function() {
        if(this.className == "aparece" && (this.value == "m1" || this.value == "m2" || this.value == "m5" || this.value == "m7" || this.value == "m8" )){
            if($('#psw1').filter(".sred").length){
                $('[name="start"]').prop('disabled', true);
                $('fieldset').removeClass('noshow');
            }
        }
    }); 
}

function show_modo(col){
    if($("#chek"+col).prop('checked') == true){
        $("#sel"+col).removeClass('desaparece').addClass('aparece');
        var m = $("#sel"+col).val(); 

        for(lin = 1; lin <= 10; lin++) {
            $("#l"+lin+"c"+col+"m0").addClass('desaparece');
            $("#l"+lin+"c"+col+m).removeClass('desaparece');
        }
    }
    else {
        $("#sel"+col).removeClass('aparece').addClass('desaparece');

        for(lin = 1; lin <= 10; lin++) {
            $("#l"+lin+"c"+col+"m1").addClass('desaparece');
            $("#l"+lin+"c"+col+"m2").addClass('desaparece');
            $("#l"+lin+"c"+col+"m3").addClass('desaparece');
            $("#l"+lin+"c"+col+"m4").addClass('desaparece');
            $("#l"+lin+"c"+col+"m5").addClass('desaparece');
            $("#l"+lin+"c"+col+"m6").addClass('desaparece');
            $("#l"+lin+"c"+col+"m7").addClass('desaparece');
            $("#l"+lin+"c"+col+"m8").addClass('desaparece');
            $("#l"+lin+"c"+col+"m0").removeClass('desaparece');
        }
    }
    check_button_start(); 
}

function change_modo(col){
    var m = $("#sel"+col).val();

    for(lin = 1; lin <= 10; lin++) {
        $("#l"+lin+"c"+col+"m1").addClass('desaparece');
        $("#l"+lin+"c"+col+"m2").addClass('desaparece');
        $("#l"+lin+"c"+col+"m3").addClass('desaparece');
        $("#l"+lin+"c"+col+"m4").addClass('desaparece');
        $("#l"+lin+"c"+col+"m5").addClass('desaparece');
        $("#l"+lin+"c"+col+"m6").addClass('desaparece');
        $("#l"+lin+"c"+col+"m7").addClass('desaparece');
        $("#l"+lin+"c"+col+"m8").addClass('desaparece');

        $("#l"+lin+"c"+col+m).removeClass('desaparece');
    }
    check_button_start();
}

function status_pwd(){
    if($('#psw1').val().length == 16){
        $('#psw1').removeClass('sred').addClass('sgreen');
    }
    else{
        $('#psw1').removeClass('sgreen').addClass('sred');
    }
    check_button_start();
}

function lines_option(){
    if(document.getElementById('opcao_saveLines').value == "lSubset") {
        $('#subset_lines').show();
        $('#random_lines').hide();
    } 
    else if(document.getElementById('opcao_saveLines').value == "lRandom") {
        $('#random_lines').show();
        $('#subset_lines').hide();
    }
    else {  
        $('#random_lines').hide();
        $('#subset_lines').hide();

        $('#lf').val(1);        
        $('#lu').val($('#lu').attr("max"));
    }
}