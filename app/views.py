# from pyexpat.errors import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views.generic import CreateView, TemplateView, View, ListView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import History, Profile
from .forms import CreateUserForm
import requests
from django.db.models import Sum
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist




def logout_view(request):
    logout(request)
    return redirect('login') 

def getBalance(user):
    # pass # this line can be deleted 
    deposits = History.objects.filter(user=user, type='deposit').aggregate(total=Sum('amount'))['total'] or 0
    withdrawals = History.objects.filter(user=user, type='withdraw').aggregate(total=Sum('amount'))['total'] or 0
    return deposits - withdrawals
    # Write a function that finds the user's balance and returns it with the float data type. 
    # To calculate the balance, calculate the sum of all user's deposits and the sum of all withdrawals.
    # Then subtract the withdrawal amount from the deposit amount and return the result.
    # '''
def getCurrencyParams():
        # The URL for the API endpoint
    url = "https://fake-api.apps.berlintech.ai/api/currency_exchange"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            formatted_list = [(currency, f"{currency} ({rate})") for currency, rate in data.items()]
            return [data, formatted_list]
        else:
            return [None, None]
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return [None, None]
    
    # pass # this line can be deleted 
    # '''
    # Write a function that makes a GET request to the following address 
    # https://fake-api.apps.berlintech.ai/api/currency_exchange

    # if the response code is 200 return a list of two values:
    # - a dictionary of data that came from the server
    # - a list of strings based on the received data 
    # mask to form the string f'{currency} ({rate})'.
    # example string: 'USD (1.15)'

    # if the server response code is not 200 you should 
    # return the list [None, None]
    # '''


class CreateUserView(CreateView):
    model = User
    form_class = CreateUserForm
    template_name = 'app/create_account.html'
    success_url = reverse_lazy('login')
    def form_valid(self, form):
        return super().form_valid(form)
    
    
    # '''
    # Finalize this class. It should create a new user.
    # The model should be the User model
    # The CreateUserForm model should be used as a form.
    # The file create_account.html should be used as a template.
    # If the account is successfully created, it should redirect to the page with the name login
    # '''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['username'] = self.request.user.username
        # '''
        # If the user is authenticated, then add the 'username' key with the value of username to the context.
        # '''
        return context

class CustomLoginView(LoginView):
    template_name = 'app/login.html'
    success_url = reverse_lazy('main_menu')
    # '''
    # Modify this class. 
    # specify the login.html file as the template
    # if authentication is positive, add redirect to main_menu page
    # '''

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['username'] = self.request.user.username
        # '''
        # If the user is authenticated, then add the 'username' key with the value of username to the context.
        # '''
        return context

class MainMenuView(LoginRequiredMixin, TemplateView):
    template_name = 'app/main_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['username'] = self.request.user.username
        # '''
        # If the user is authenticated, then add the 'username' key with the value of username to the context.
        # '''
        return context

class BalanceOperationsView(LoginRequiredMixin, View):
    template_name = 'app/operations.html'

    def getBalance(self, user):
        deposits = History.objects.filter(user=user, type='deposit').aggregate(total=Sum('amount'))['total'] or 0
        withdrawals = History.objects.filter(user=user, type='debit').aggregate(total=Sum('amount'))['total'] or 0
        return deposits - withdrawals
    
    def get(self, request):
        context = {
            'balance': self.getBalance(request.user),
            'username': request.user.username,
        }
        return render(request, self.template_name, context)
        # pass # this line can be deleted 
        # '''
        # This method should return the page given in template_name with a context.

        # Context is a dictionary with balance and username keys.
        # The balance key contains the result of the getBalance function
        # username contains the username of the user.
        # '''


    def post(self, request):
        try:
            amount = float(request.POST.get('amount', 0))
        except ValueError:
            messages.error(request, "Invalid amount.")
            return redirect('balance_operations')  # Redirect back to the operations page on invalid input

        operation_type = request.POST.get('operation')
        user = request.user
        balance = self.getBalance(user)

        # Validate operation type
        if operation_type not in ['withdraw', 'deposit']:
            messages.error(request, "Invalid operation type.")
            return redirect('balance_operations')  # Redirect back on invalid operation

        if operation_type == 'withdraw':
            if amount > balance:
                status = 'failure'
                messages.error(request, "Insufficient funds for withdrawal.")
            else:
                status = 'success'
                messages.success(request, "Withdrawal successful.")
        elif operation_type == 'deposit':
            status = 'success'
            messages.success(request, "Deposit successful.")
        
        

        History.objects.create(
            status=status,
            amount=amount,
            type=operation_type,
            user=user
        )
        
        context = {
            'balance': self.getBalance(user),
            'username': user.username,
        }
        
        return render(request, self.template_name, context)

        # pass # this line can be deleted 
        # '''
        # This method should process a balance transaction.
        # For this purpose it is necessary to add an entry to the History model. 
        
        # status - if the amount on the account is not enough when attempting to withdraw funds, the status is failure, otherwise withdraw
        # amount - amount of operation, obtained from the form
        # type - type of operation (withdraw/deposit), the value is obtained from the form.
        # user - object of the current user

        # This method should return the page given in template_name with a context.

        # Context is a dictionary with balance and username keys.
        # The balance key contains the result of the getBalance function (after account update)
        # username contains the username of the user.
        # '''

class ViewTransactionHistoryView(LoginRequiredMixin, ListView):
    model = History
    template_name = 'app/history.html'
    context_object_name = 'transactions'
    ordering = ['-datetime']

    def get_queryset(self):
        return History.objects.filter(user=self.request.user).order_by('-datetime')
        # '''
        # This method should return the entire transaction history of the current user
        # '''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        # '''
        # Add the 'username' key with the value of username to the context.
        # '''
        return context

class CurrencyExchangeView(LoginRequiredMixin, View):
    template_name = 'app/currency_exchange.html'
    empty_context = {'currency_choices': [], 'amount': None, 'currency': None, 'exchanged_amount': None}

    def get(self, request):
        _, currency_choices = getCurrencyParams()
        context = {
            **self.empty_context,
            'currency_choices': currency_choices,
            'username': request.user.username
        }
        # '''
        # Generate a context variable with all values from empty_context and the converted values of currency_choices and username
        # currency_choices contains the value of the currency_choices variable
        # username contains the name of the current user
        # '''
        return render(request, self.template_name, context)

    def post(self, request):
        data, currency_choices = getCurrencyParams()
        try:
            amount = float(request.POST.get('amount'))
        except (TypeError, ValueError):
            amount = None
        
        currency = request.POST.get('currency')
        if data is None or amount is None or currency not in data:
            context = {
                **self.empty_context,
                'currency_choices': currency_choices,
                'username': request.user.username
            }
            return render(request, self.template_name, context)

        exchange_rate = data.get(currency)
        exchanged_amount = round(amount * exchange_rate, 2)
        context = {
            'currency_choices': currency_choices,
            'amount': amount,
            'currency': currency,
            'exchanged_amount': exchanged_amount,
            'username': request.user.username
        }
        return render(request, self.template_name, context)
        # '''
        #     Improve this method:
        #     1) add the process of forming the variable amount.
        #     If the amount value from the form is converted to float type, then write the amount value from the form converted to float to the amount variable. Otherwise, write None.
        #     2) add a currency variable that contains the currency value from the form.
        #     3) if the variables data or amount contain None, return page with empty context (empty_context). Otherwise, perform the following steps
        #     4) generate the exchange_rate variable by calculating the corresponding value from the data variable
        #     5) generate the exchanged_amount variable, which contains the converted currency to two decimal places.
        #     6) form a context from the previously created variables and return a template with it.
        # '''

