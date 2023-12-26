import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import os 
import streamlit as st
from dotenv import load_dotenv
from mysql_class import MySQLDatabase
load_dotenv()

st.set_page_config(page_title="Lodge Booking Assistant", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
GPT_MODEL = "gpt-4-1106-preview"

openai.api_key = os.environ["OPENAI_API_KEY"]

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


## Functions
def book_tickets(name, location, arrival_date, departure_date, suite_category, suite_sub_category):
    mdb = MySQLDatabase()
    try:
        print('--'*30)
        print(name, location, arrival_date, departure_date, suite_category, suite_sub_category)
        print('--'*30)
        b_id= mdb.insert_data('booking', ['name', 'location','arrival_date', 'depart_date', 'category', 'subcategory', 'is_active'],
                        [name, location, arrival_date, departure_date, suite_category, suite_sub_category, 1])
    except Exception as e:
        return f"some error occured while making booking: {e}"
    return f"You Booking is Successful! Your Booking Reference ID is: BNO_GWR_{b_id}. Your passes are shared on email."

def cancel_booking(booking_number, **kwargs):
    mdb = MySQLDatabase()
    try:
        booking_number = booking_number[8:]
        print(booking_number)
        b_id= mdb.update_data('booking', 'is_cancel', 1, 'b_id' , booking_number)
    except Exception as e:
        return f"some error occured while making booking: {e}"
    return f"Your Booking with Booking Number: BNO_GWR_{booking_number} is cancelled successfully! You will receive confirmation email shortly."

#this will be the function to edit bookings
def edit_booking(booking_number, **kwargs):
    mdb = MySQLDatabase()
    try:
        booking_number = booking_number[8:]
        print(booking_number)
        b_id= mdb.update_data('booking', 'is_cancel', 1, 'b_id' , booking_number)
    except Exception as e:
        return f"some error occured while making booking: {e}"
    return f"Your Booking with Booking Number: BNO_GWR_{booking_number} is cancelled successfully! You will receive confirmation email shortly."
## Tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "book_tickets",
            "description": "When user is ready to finalize the booking only then use this function. Otherwise keep interacting with user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of person, eg: Sarmad Afzal",
                    },
                    "location": {
                        "type": "string",
                        "description": "Location of the resort/lodge, eg: Gurnee, IL",
                    },
                    "arrival_date" : {
                        "type" : "string",
                        "format" : "datetime",
                        "description": "Date of arrival of the customer at resort, eg: 12 Aug, 2023"
                    },
                    "departure_date" : {
                        "type" : "string",
                        "format" : "datetime",
                        "description": "Date of departure of the customer from the resort, eg 30 Aug, 2023"
                    },
                    "suite_category" : {
                        "type" : "string",
                        "enum" : ["Standard", "Themed"],
                        "description" : "Type of the suite, for eg: Standard or Themed"
                    },
                    "suite_sub_category": {
                        "type": "string",
                        "enum" : ['Deluxe Family Suite', 'Family Suite', 'Deluxe Queen Suite', 'Wolf Den Suite', 'Junior Cabin Suite'],
                        "description" : "Sub-type or sub-category of the suite for eg: Deluxe Family Suite or Wold Den Suite"
                    } 
                },
                "required": ["name", "location", "arrival_date", "departure_date", "suite_category", "suite_sub_category"],
            },
        },

        
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Usefulful when user ask to cancel the booking. You must have Booking Number beforehand asked from user to call this function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_number": {
                        "type": "string",
                        "description": "Booking Number, it is the reference number to cancel the booking.",
                    },
                },
                "required": ["booking_number"],
            },
        },

        
    }
]

if 'messages' not in st.session_state:
        st.session_state.messages = ['0']

def chat_tools_func(query):

    System_prompt = f"""
    You are an AI Travel Booking Assistant of Mystic Pines Resort. You will be assisting a customer for making booking.    
    Do directly ask for books, interact in a creative way. Show them what options we have for the lodges, ask if they want to see the images and detail features. Only then ask for booking.

    To book a lodge, you must know following important information. One by one in the conversation ask the user for the following information.
    - Full Name
    - Location of the Lodge
    - Arrival Date
    - Departure Date
    - Type of Suite
    - Sub type of Suite

    Following are details about the suites offered at Great Wold Lodge. Always display them in bullet points.
    There are 2 different types of suites and each has sub type / sub category with respective features:
    1 - Standard
        a - Deluxe Family Suite
            Features:
                Sleeps 4-6
                Balcony suite includes two queen beds as well as a semi-private living area with a twin-size sofa sleeper.

                2 Queen beds
                1 Twin sleeper sofa
                1 Semi-private living area
                1 Balcony/Patio
                1 Full bath
                TV
            Details URL: https://www.enchantedgroveresort.com/suites/standard/deluxe-family-suite-balcony 
            Image URL: [https://www.bestwesternmidway.com/wp-content/uploads/2018/03/doublebedroom-1024x576.jpg, https://libraryhotel.com/_novaimg/galleria/1332639.jpg ,https://www.grandwailea.com/sites/default/files/styles/gallery/public/2023-05/King%20Garden%20View.jpg]

        b - Family Haven Suite
            Features:
                Sleeps 4-6
                Suite featuring two queen beds as well as a living area.

                2 Queen beds
                1 Full sleeper sofa
                1 Full bath
                1 TV
                Hair dryer
                Coffee maker
            Details URL: https://www.enchantedgroveresort.com/suites/standard/family-haven-suite
            Image URL: [https://www.bestwesternmidway.com/wp-content/uploads/2018/03/doublebedroom-1024x576.jpg, https://libraryhotel.com/_novaimg/galleria/1332639.jpg ,https://www.grandwailea.com/sites/default/files/styles/gallery/public/2023-05/King%20Garden%20View.jpg]

        c - Deluxe Forest Suite
            Features:
                Sleeps 4-5
                Standard suite includes two queen beds as well as a living area with a twin-size sofa sleeper.

                2 Queen beds
                1 Twin sleeper sofa
                1 Full bath
                TV
                Mini-fridge
                Coffee maker
            Details URL: https://www.enchantedgroveresort.com/suites/standard/deluxe-forest-suite
            Image URL: [https://www.bestwesternmidway.com/wp-content/uploads/2018/03/doublebedroom-1024x576.jpg, https://libraryhotel.com/_novaimg/galleria/1332639.jpg ,https://www.grandwailea.com/sites/default/files/styles/gallery/public/2023-05/King%20Garden%20View.jpg]

    2 - Themed
        a - Fairy Tale Retreat
            Features: 
                Sleeps 4-6
                Standard suite featuring a magical fairy tale-themed sleeping area.
                1 Queen bed
                1 Full sleeper sofa
                1 Bunk bed
                1 Full bath
                2 TVs
                Mini-fridge
            Details URL: https://www.enchantedgroveresort.com/suites/themed/fairy-tale-retreat
            Image URL: [https://i.ibb.co/mSPdv7J/fairytale1.jpg, https://i.ibb.co/9WmW9Yb/fairytale2.jpg]

        b - Woodland Cabin Escape
            Features:
                Sleeps 4-6
                Standard suite features a cozy woodland cabin-themed sleeping area.

                1 Queen bed
                1 Day bed
                1 Bunk bed
                1 Twin sleeper sofa
                1 Full bath
                2 TVs
            Details URL: https://www.enchantedgroveresort.com/suites/themed/woodland-cabin-escape
            Image URL: [https://i.ibb.co/mSPdv7J/fairytale1.jpg, https://i.ibb.co/9WmW9Yb/fairytale2.jpg]


               
    If in any case you come across a question for which you cannot find details, please propose the URL to user.
    
    Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
    Before finalizing the booking and calling the function. Make sure to ask the user for confirmation by showing all the details.
    
    You should never ask them for cancellation of bookings. But Only is user ask for cancellation.
    Please ask them first for booking_number, once you have the booking number then ask them for confirmation and only then cancel the booking using cancel_booking function.
    """

    
    #st.error(st.session_state.messages)
    st.session_state.messages[0] = {"role": "system", "content": System_prompt}
    st.session_state.messages.append({"role": "user", "content": query})
    chat_response = chat_completion_request(
        st.session_state.messages, tools=tools, tool_choice='auto', model='gpt-4-1106-preview'
    )

    json_response = chat_response.json()
    #st.write(json_response)
    text_response1 =  json_response['choices'][0]['message']
    print("This is First Chat Response")
    print(text_response1)
    tool_calls = None
    second_response2 = None

    try:
        tool_calls = json_response['choices'][0]['message']['tool_calls']
        print("This is to see if there is any Tool Call")
        print(tool_calls)
    except Exception as e:
        pass

    if isinstance(tool_calls, list):
        print("there is a tool call")
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "book_tickets": book_tickets,
            "cancel_booking" : cancel_booking
        }  # only one function in this example, but you can have multiple
        st.session_state.messages.append(text_response1)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call['function']['arguments'])
            if function_name == "book_tickets":
                function_response = function_to_call(
                    name=function_args.get("name"),
                    location=function_args.get("location"),
                    arrival_date=function_args.get("arrival_date"),
                    departure_date=function_args.get("departure_date"),
                    suite_category=function_args.get("suite_category"),
                    suite_sub_category=function_args.get("suite_sub_category")
                )
            elif function_name == "cancel_booking":
                function_response = function_to_call(
                    booking_number=function_args.get("booking_number"),
                )

            st.session_state.messages.append(
                {
                    "tool_call_id": tool_call['id'],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = chat_completion_request(
            model="gpt-4-1106-preview",
            messages=st.session_state.messages,
        )  # get a new response from the model where it can see the function response

        print("This is the second response after calling the tool")
        print(second_response.json())
        second_response2 = second_response.json()["choices"][0]["message"]

        print(second_response2)

    # assistant_message = chat_response.json()["choices"][0]["message"]
    # tool_call = assistant_message.tool_calls
    # print(tool_call)
    # messages.append(assistant_message)
    # print(assistant_message)
    #st.write(messages)
    return text_response1, second_response2


# query = st.text_input("Book now")
# if query:
#     with st.spinner():
#         first, second = chat_tools_func(query)
#         st.session_state.messages.append(first)
#         #st.write(first)
#         st.write("First Response:", first['content'])        
#         st.write("Second Response:", second['content'])


st.title("Lodge Booking Assistant")
if "myimage" not in st.session_state:
    st.session_state.myimage = True

if st.session_state.myimage:
    st.image("images/image.png")

if "sugg_qns" not in st.session_state:
    st.session_state.sugg_qns = True




# Initialize chat history
if "messages_st" not in st.session_state:
    st.session_state.messages_st = []

# Display chat messages from history on app rerun
for messages_st in st.session_state.messages_st:
    with st.chat_message(messages_st["role"]):
        st.markdown(messages_st["content"])

sugg_prompt = None

if st.session_state.sugg_qns:
    s1, s2, s3 = st.columns([1,1,1])
    with s1:
        ss1 = st.button("Recommend me lodges for Christmas")
        if ss1: 
            sugg_prompt = "Recommend me lodges for Christmas"
    with s2:
        ss2 = st.button("I am interest in themed stay, show me some options")
        if ss2:
            sugg_prompt = "I am interest in themed stay, show me some options"
    with s3:
        ss3 = st.button("Show me images of Deluxe Queen Suite")
        if ss3:
            sugg_prompt = "Show me images of Deluxe Queen Suite"

# React to user input
if prompt := st.chat_input("What is up?") or sugg_prompt:
    
    st.session_state.myimage = []
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages_st.append({"role": "user", "content": prompt})
    with st.spinner(" "):
        first, second = chat_tools_func(prompt)
        
        st.session_state.sugg_qns = []
        if second is None:
            response = first
        else:
            response = second
        st.session_state.messages.append(response)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response['content'])
    # Add assistant response to chat history
    st.session_state.messages_st.append({"role": "assistant", "content": response['content']})
        

with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        db=MySQLDatabase()
        st.metric("Total Bookings Today", db.get_row_count('booking'), db.get_row_count('booking'))
    
    with col2: 
        db=MySQLDatabase()
        st.metric("Total Cancellations Today", db.cancelled_count(), db.cancelled_count())
    
    st.subheader("These are the records of the booking made")
    st.caption("Live quering from MySQl DB")
    db = MySQLDatabase()
    st.dataframe(db.fetch_all_rows('booking'))