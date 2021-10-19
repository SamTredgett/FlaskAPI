import pydantic
""" 
    Our data models are structured using pydantic to affirm type conforming
    and to provide validation options.
"""
class Sender(pydantic.BaseModel):
    """ Sender objects store data regarding the location of the sender """
    name: str
    street_address: str
    city: str
    country_code: str

class Recipient(pydantic.BaseModel):
    """ 
        Recipient objects store data for the recipient
        this data will be processed more in the API
    """
    name: str
    street_address: str
    city: str
    country_code: str

class Order(pydantic.BaseModel):
    """ 
        Order objects contain the unique information for each order
        This information is vital to the API processing
        they also contain both a sender and recipient as part of their structure
    """
    sender: Sender
    recipient: Recipient
    value: str
    despatch_date: str
    contents_declaration: str = pydantic.Field(..., alias='contents declaration')
    insurance_required: bool
    tracking_reference: str


