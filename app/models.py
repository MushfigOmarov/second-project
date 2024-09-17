from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class History(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    datetime = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f'{self.user.username} - {self.get_type_display()} - {self.amount} - {self.get_status_display()}'


    


    

    # '''
    # Create a History model with the following set of fields

    # status - a string with a maximum length of 10. The value must be success or failure.
    # The aliases should be Success and Failure respectively.

    # amount - a fractional number. The maximum number of digits is 10, 2 decimal places. Default value is 0.00
    
    # type - a string with maximum length 10. The value must be deposit or debit.
    # The aliases should be Deposit and Debit respectively.
    
    # user - the foreign key associated with User. The relationship type is one to many. 
    
    # datetime - the point in time when the record was created.

    # Add a string mapping of the entity in the format:
    # 'User Name - Transaction Type - Transaction Amount - Status'
    
    # Example:
    # 'Tom - withdrawal - 100 - success'.
    # '''