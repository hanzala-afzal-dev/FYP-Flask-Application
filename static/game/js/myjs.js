
$(document).ready(function(){
	$('#btn-submit').click(function(){
		var node1 = $('#node1').val();
		var node2 = $('#node2').val();

		var n1_obj=document.getElementById('node1');
		var n2_obj=document.getElementById('node2');

		if(!n1_obj.checkValidity() || !n2_obj.checkValidity())
		{
			$("#submit-hidden").click();
		}
		else{
			$.ajax({
				url: '/predict',
				data: $('form').serialize(),
				type: 'POST',
				success: function(response){
					if(response=="-1")
					{
						window.location.href="login/index?res=Login"
					}
					else if(response=="-2")
					{
						$('#btn-submit').show();
						$('#loader-gif').hide();
					}
					else
					{
						$('#comeent').html(response);
						$('#btn-submit').show();
						$('#loader-gif').hide();
					}
					
				},
				error: function(error){
					console.log(error);
				},
				beforeSend: function(){
					$('#btn-submit').hide();
					
					$('#loader-gif').removeAttr("Hidden");
					$('#loader-gif').show();
					$('#comeent').html("");
				}
			});

		}

	});
});
