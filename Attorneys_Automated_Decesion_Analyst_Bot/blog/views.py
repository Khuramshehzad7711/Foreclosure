from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .forms import UserResponseForm


# Define questions and their criteria weights
questions = [
    # Data Set II: Property Ownership (PO)
    {"question": "Are you the property owner? If not, then what is your relation to the owner?", "weights": [0.534, -1.068, 0, 0]},
    {"question": "What type of property has been foreclosed? (Options: Residential Property, Commercial Property, RV, Boat)", "weights": [0.534, 0, 0, 0]},
    {"question": "Does the property owner not speak, read, write, or understand the English language?", "weights": [0.534, 0, 0, 0]},
    {"question": "Is the property owner medically or legally blind?", "weights": [0.445, 0, 0, 0]},
    {"question": "Does the property owner have any learning disability that might prevent him/her from understanding property documents they signed?", "weights": [0.534, 0, 0, 0]},
    {"question": "Has the property owner reported any forged signatures on the property documents?", "weights": [0.356, -0.356, 0, 0]},

    # Data Set III: Foreclosure Process (FP)
    {"question": "What is the property address that underwent foreclosure?", "weights": [2.4, -2.4, 0, 0]},
    {"question": "Did the property owner receive written notice in postal mail or email of default and intent to accelerate from the lender?", "weights": [-2.4, 9.6, 4.8, 0]},
    {"question": "Did the notice provide at least 30 days from the date of the notice to the date of the proposed foreclosure?", "weights": [9.6, -9.6, 0, 0]},
    {"question": "Did the published notice contain any errors or deficiencies?", "weights": [-2.4, 7.2, 0, 0]},
    {"question": "Was the property sold below market value, or was bidding restricted?", "weights": [-7.2, 3.6, 0, 0]},
    {"question": "Did the owner receive a notice from the bank, and if so, did the owner default on any of the three conditions mentioned in the notice?", "weights": [-30, 15, 0, 0]},

    # Data Set IV: Property Advertisement (Property_Ad) (PA)
    {"question": "Describe the methods used by the lender to advertise the property for sale?", "weights": [0.178, -0.089, 0, 0]},
    {"question": "Were these advertising methods explicitly laid out in the terms of the agreement or any other contractual instrument?", "weights": [0.089, -0.089, 0.178, 0]},
    {"question": "Did the advertisements accurately represent the condition and value of the property?", "weights": [0.178, -0.089, 0, 0]},

    # Data Set V: Property Sale (Property_Sale) (PS)
    {"question": "How did you determine the initial asking price of the property, and was this in line with market rates?", "weights": [0.089, -0.089, 0, 0]},
    {"question": "Was the sale open to the public, and if so, were reasonable steps taken to invite competitive bids?", "weights": [0.089, -0.089, 0, 0]},
    {"question": "Were there any conditions or contingencies imposed on the sale that were not outlined in the original agreement?", "weights": [0.089, -0.089, 0, 0]},
    {"question": "Did the lender/lender's agent provide all necessary disclosures regarding the property, such as any defects or liens, to prospective buyers?", "weights": [0.089, -0.089, 0, 0]},
    {"question": "At any point, was there any conflict of interest in conducting the sale?", "weights": [0.089, -0.089, 0, 0]},

    # Data Set VI: Good Faith (GF)
    {"question": "Can you provide any evidence to support that the lender or lender's representative have acted impartially or not acted in good faith throughout the sales process?", "weights": [0.089, -0.089, 0, 0]},
    {"question": "Were there any actions taken by the lender or the lender's representatives or decisions made during the sale that could be construed as acting in bad faith or in a deceptive manner?", "weights": [0.089, -0.089, 0, 0]},
    {"question": "Has the lender or the lender's agent you dealt with ever been investigated or sanctioned for not conducting a property sale in good faith?", "weights": [0.089, -0.089, 0, 0]},

    # Data Set I: Core Information (CI)
    {"question": "Write your contact information here so that we can reach you?", "weights": [0.3, 0, 0, 0]}
]



# Create a variable to keep track of the current question index
current_question_index = -1

# Initialize a dictionary to store responder's answers
responder_answers = {}

def index(request):
    return render(request, 'blog/index.html')

def specific(request):
    return HttpResponse("List1")

def getResponse(request):
    global current_question_index
    global responder_answers

    if request.method == 'GET':
        userMessage = request.GET.get('userMessage')

        if current_question_index < len(questions):
            current_question = questions[current_question_index]
            current_question_index += 1

            responder_answers[current_question["question"]] = userMessage

            if current_question_index < len(questions):
                next_question = questions[current_question_index]
                return JsonResponse({'botResponse': next_question["question"]})
            else:
                # Calculate the responder's score based on their answers and weights
                score = calculate_responder_score(responder_answers, questions)

                # Use the last response as the responder's name
                responder_name = userMessage

                # Create the form with the data
                form = UserResponseForm({
                    'responder_name': responder_name,
                    'question': current_question["question"],
                    'user_answer': userMessage,
                    'score': score
                })

                if form.is_valid():
                    form.save()
                    if score > 0:
                        return JsonResponse({'botResponse': f'Your confidence score is {round(score)}. Your application has been submitted. An attorney will contact you for one free consultation if you provided your contact information.'})
                    else:
                        return JsonResponse({'botResponse': 'Your application has been submitted.'})
                else:
                    return JsonResponse({'botResponse': 'There was an error with your submission. Please check your answers and try again.'})

        else:
            if userMessage.lower() != '':
                # Reset the conversation to start over
                current_question_index = 0
                responder_answers = {}
                return JsonResponse({'botResponse': questions[current_question_index]["question"]})
            else:
                return JsonResponse({'botResponse': 'No more questions. Type "reset" to start over.'})



def calculate_responder_score(responder_answers, questions):
    score = 0

    for question in questions:
        question_text = question["question"]
        user_answer = responder_answers.get(question_text, "").lower()
        weights = question["weights"]

        if "no" in user_answer:
            score += weights[1]
        elif "yes" in user_answer:
            score += weights[0]
        elif "not sure" in user_answer:
            score += weights[2]
        else:
            score += weights[3]
    
    return score 


