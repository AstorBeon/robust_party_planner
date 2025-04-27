import random
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

#image = Image.open('dominik_cut.png')


transport_min=-1
transport_max=1
accom_min=-1
accom_max=-1
foods_min = -1
foods_max=-1
NAME = "Alex"
PARTYTYPE = "Bachelor"

st.set_page_config(page_title=f"{NAME}'s {PARTYTYPE} Party - cost breakdown calculator",layout="wide")#, page_icon = st.image(image))


if 'activities' not in st.session_state:
    st.session_state['activities'] = [("Paintball",150)]
    st.session_state['activities_objs'] = []

if "is_new_activity_open" not in st.session_state:
    st.session_state['is_new_activity_open']=False

random_activities=["Washing my car","Doing pushups","Drinking liquids on first sight","Trying to lick own elbow",
                   "Petting dogs","Speedrunning blood donations","Watching cartoons","Digging tunnel to China","Cracking"
                                                                                                               "joints"]

#st.set_page_config(layout="wide")
st.title(f"{NAME}'s {PARTYTYPE} party - Cost breakdown")
limit= st.text_input('Amount to be spent (initial assumption)', '600')
st.subheader('Transportation')


option = st.selectbox(
     'How will we travel?',
     ('Train', 'Car','No travel - staying in city'))
trans_col1, trans_col2 = st.columns(2)
if(option == "Train"):

    with trans_col1:
        cost_of_transport = st.number_input('Cost of the ticket (two ways)', 150)
    with trans_col2:
        cost_of_transport_on_site= st.number_input('Cost of transportation on site', 20)
    transport_total = int(cost_of_transport) + int(cost_of_transport_on_site)
elif option == 'No travel - staying in city':
    cost_of_transport = st.text_input('Cost of local tickets', '10')
else:
    adv = st.checkbox('Advanced transport calculations')
    if not adv:
        with trans_col1:
            cost_of_transport_fuel = st.text_input('Cost of fuel:', '250')
        with trans_col2:
            cost_of_transport_on_site = st.text_input('Cost of transportation on site', '20')
        transport_total = int(cost_of_transport_fuel) + int(cost_of_transport_on_site)
    else:
        #Advanced cost calculating for car
        with trans_col1:
            cost_of_transport_litres_per_100km = st.number_input('Litres of fuel 100km:', 10)
            cost_of_transport_cost_of_litre = st.number_input("Cost of single litre:", 7)
            cost_of_transport_length = st.number_input('Length of whole route(km) - two ways:', 356)
        with trans_col2:
            cost_of_transport_highway_fee = st.number_input('Cost of highway fees:', 20)
            cost_of_transport_on_site = st.number_input('Cost of transportation on site', 20)
        transport_total = float(cost_of_transport_highway_fee) + \
                          float(cost_of_transport_length) / 100 * float(cost_of_transport_cost_of_litre) *\
                          float(cost_of_transport_litres_per_100km) + float(cost_of_transport_on_site)

        cost_of_transport_deviation = st.number_input('Deviation/Reserve (%):', 10)
        cost_of_transport_deviation_calculation = transport_total/int(cost_of_transport_deviation)
        st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f'<p class="big-font">Including {cost_of_transport_deviation}% deviation, total cost of transport is: ---> {transport_total + transport_total/float(cost_of_transport_deviation)}</p>', unsafe_allow_html=True)

st.subheader('Accomodation')
acom_col1, acom_col2 = st.columns(2)
with acom_col1:
    cost_of_accomodation = st.number_input('Cost of accomodation(total):', 220)
with acom_col2:
    cost_of_accomodation_deviation = st.number_input('Deviation/Reserve(%):', 5)
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)
try:
    accomodation_total_deviation_calculation =int(cost_of_accomodation) / float(cost_of_accomodation_deviation)
    accom_min=int(cost_of_accomodation)-accomodation_total_deviation_calculation
    accom_max=int(cost_of_accomodation)+accomodation_total_deviation_calculation
except Exception:
    accomodation_total_deviation_calculation=0
    accom_min,accom_max=int(cost_of_accomodation),int(cost_of_accomodation)
if accomodation_total_deviation_calculation==0:
    st.markdown(
        f'<p class="big-font">Total cost of transport is: ---> {cost_of_accomodation}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<p class="big-font">Including {cost_of_accomodation_deviation}% deviation, total cost of transport is between : ---> {int(cost_of_accomodation)-accomodation_total_deviation_calculation} and {int(cost_of_accomodation)+accomodation_total_deviation_calculation}</p>',
        unsafe_allow_html=True)


st.subheader('Food & Drinks')
food_col1, food_col2 = st.columns(2)
with food_col1:
    cost_of_food = st.number_input('Cost of food', 160)
with food_col2:
    cost_of_drinks = st.number_input('Cost of drinks (alc)', 160)
total_cost_foods_drinks = int(cost_of_food) + int(cost_of_drinks)
cost_of_food_deviation = st.text_input('Deviation:', '0')

try:
    foods_total_deviation_calculation =int(total_cost_foods_drinks) / float(cost_of_food_deviation)
    foods_min=total_cost_foods_drinks-foods_total_deviation_calculation
    foods_max=total_cost_foods_drinks+foods_total_deviation_calculation
except Exception:
    foods_total_deviation_calculation=0
    foods_min,foods_max=total_cost_foods_drinks,total_cost_foods_drinks
if foods_total_deviation_calculation==0:
    st.markdown(
        f'<p class="big-font">Total cost of foods and drinks is: ---> {total_cost_foods_drinks}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<p class="big-font">Including {cost_of_food_deviation}% deviation, total cost of foods and drinks is between : ---> {int(total_cost_foods_drinks)-foods_total_deviation_calculation} and {int(total_cost_foods_drinks)+foods_total_deviation_calculation}</p>',
        unsafe_allow_html=True)



st.subheader("Activities")

def generate_knowledge_summary():
    pass
count=0
initial = True

def delete_from_activities(index):
    if initial:

        return
    del st. session_state['activities'][index]



if 'activities' not in st.session_state.keys():
    st.session_state['activites'] = {}
for key,val in st.session_state['activities']:
    col_1, col_2 = st.columns(2)
    with col_1:
        x = st.number_input(key,val)
    st.session_state['activities_objs'].append(x)
    st.session_state['activities'][count]=(key,x)
    #st.button(f"DELETE - {key.split(' ')[0]}",on_click=delete_from_activities)

    with col_2:
        st.text("   ")
        st.text("   ")
        st.button(f"""DELETE -\n {key}""",on_click=delete_from_activities,args=(count,))
    count+=1


def add_activity_panel():
    st.session_state['is_new_activity_open']=True

if (st.session_state['is_new_activity_open']):
    if "temp new activity" not in st.session_state:
        st.session_state["temp new activity"]=random.choice(random_activities)
    act_name = st.text_input(f"New activity name: ",st.session_state["temp new activity"],)

    def add_activity():
        st.write(act_name)
        if act_name:
            st.write(act_name)
        st.session_state['activities'].append((act_name,0))
        #####st.session_state['activities_objs'].append(act_name)
        st.session_state['is_new_activity_open'] = False


    st.button("Approve new activity",on_click=add_activity)
st.button("Add new activity",on_click=add_activity_panel)

initial=False

activities_cost = sum([int(x[1]) for x in st.session_state['activities']])

total_cost = transport_total + activities_cost+int(cost_of_accomodation) + total_cost_foods_drinks

st.markdown("""
<style>
.big-font-res {
    font-size:60px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def generate_knowledge_summary():
    st.subheader("Summary:")
    knowledge_summary =  f"Way of transportation: {option} ->"

    try:
        cost_of_transport_deviation_calculation
        transport_min =transport_total - cost_of_transport_deviation_calculation
        transport_max = transport_total + cost_of_transport_deviation_calculation
        knowledge_summary += f" {round(transport_min,2)} <-> {round(transport_max,2)}<br>"


    except Exception:
        knowledge_summary += f"{transport_total}<br>"
        transport_min,transport_max = transport_total,transport_total

    knowledge_summary+=f"Accomodation -> "
    if accomodation_total_deviation_calculation !=0:
        accom_min = int(cost_of_accomodation)-accomodation_total_deviation_calculation
        accom_max=int(cost_of_accomodation)+accomodation_total_deviation_calculation
        knowledge_summary+=f"{accom_min} <-> {accom_max}<br>"
    else:
        knowledge_summary+=f"{cost_of_accomodation}<br>"

    knowledge_summary+=f"Foods & drinks -> "
    if(foods_total_deviation_calculation!=0):
        foods_min = total_cost_foods_drinks-foods_total_deviation_calculation
        foods_max = total_cost_foods_drinks+foods_total_deviation_calculation
        knowledge_summary+=f"{foods_min} <-> {foods_max}<br>"
    else:
        knowledge_summary+=f"{total_cost_foods_drinks}<br>"

    knowledge_summary+=f"Activities -> {activities_cost}:<br>"
    for activity in st.session_state['activities']:
        knowledge_summary += f">>>{activity[0]} -> {activity[1]}<br>"

    #knowledge_summary+=f"Total for activities is: {activities_cost}"
    return knowledge_summary

#knowledge_summary=generate_knowledge_summary()
def show_summary():
    #st.write(generate_knowledge_summary())
    st.markdown(
    f'<p class="big-font">{generate_knowledge_summary()}</p>',
    unsafe_allow_html=True)


#st.button(f"Generate sumary!",on_click=show_summary)
show_summary()
true_total_cost = transport_total + int(cost_of_accomodation) + total_cost_foods_drinks+activities_cost
addition_for_bach = st.number_input(f"Percentage added for bachelor (cos  {NAME} doesn't pay)",10)
true_total_cost *= 1+float(addition_for_bach)/100

min_costs=foods_min + accom_min + transport_min + int(activities_cost)

min_costs*=1+float(addition_for_bach)/100

max_costs=foods_max + transport_max + accom_max + int(activities_cost)
max_costs*=1+float(addition_for_bach)/100

if (min_costs!=max_costs):
    st.markdown(
        f'<p class="big-font-res">Total cost is between {round(min_costs,2)} and {round(max_costs,2)}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
    f'<p class="big-font-res">Total cost is {true_total_cost}</p>',
    unsafe_allow_html=True)


if (min_costs+max_costs)/2>int(limit):
    st.error(f"Including all deviations, total cost WILL be higher than planned - from {round(min_costs-int(limit),2)} up to {round(max_costs-int(limit),2)} over the limit")
elif max_costs>int(limit):
    st.warning(
        f"Including all deviations, total cost might be higher than planned - up to {round(max_costs - int(limit),2)} over the limit")
else:
    st.success("It seems like all costs are going to be within initial assumption!")


#st.markdown("<br>",unsafe_allow_html=True)

def export_data():
    st.balloons()



st.button("Export (not yet implemented)",on_click=export_data)




st.markdown("""
<style>
.footerstyle{
    font-size:12px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)



st.markdown(
     f'<p class="footerstyle"><br>Made by: Astor Beon - v. 1.2</p>',
     unsafe_allow_html=True)



