    var quizData = {{ data|safe }};
    const question = document.getElementById('question');
    const submitBtn = document.getElementById('submit');
    const user_ans = document.getElementById('answer');

    let currentQuiz = 0;
    let score = 0;
    let response = [];


    loadQuiz();
    alert("working");
    function loadQuiz() {
    const currentQuizData = quizData[currentQuiz];

    question.innerText = currentQuizData['name'];
    }

    submitBtn.addEventListener('click', ()=>{
        let answer = user_ans.value;
    // response.push(answer);
    response[currentQuiz] = answer;
    currentQuiz++;
    alert("you have successfully completed Quiz!")

    // if (currentQuiz < quizData.length) {
    //     loadQuiz();
    // } else {
    //     alert("you have successfully completed Quiz!")
    // }
    })



    function ask_submit(){
        if (confirm("Do you want to save changes?") == true) {
            sub();
        }
    }

        var min = "{{era['duration']}}";
        var sec = '0';
function examTimer() {
            if (parseInt(sec) >0) {

			    document.getElementById("showtime").innerHTML = min+" Minutes " + sec+" Seconds";
                sec = parseInt(sec) - 1;                
                tim = setTimeout("examTimer()", 1000);
            }
            else {

			    if (parseInt(min)==0 && parseInt(sec)==0){
			    	document.getElementById("showtime").innerHTML = min+" Minutes " + sec+" Seconds";
                    alert("Your time is up! Thank You for attempting the exam!");
                    sub();
				     document.questionForm.minute.value=0;
				     document.questionForm.second.value=0;
                     

			     }

                if (parseInt(sec) == 0) {				
				    document.getElementById("showtime").innerHTML = min+" Minutes " + sec+" Seconds";					
                    min = parseInt(min) - 1;
					sec=59;
                    tim = setTimeout("examTimer()", 1000);
                }

            }
        }
