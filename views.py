    # Create your views here.
from django.template import Context, Template, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm
from django import forms
import photologue
import os

from models import * 

def success(request):
    return HttpResponse('ok')

def ipn(request):
    from utils import paypal
    paypal.ipn(request.REQUEST)
    
def clear_cart(request):
    session['cart'] = Cart() 
    
def checkout(request):
    t = loader.get_template('checkout.django')
    cart = request.session['cart']
    return HttpResponse(t.render(Context({'cart': cart})))
        

class OrderItem():
    def __init__(self, photo_id, s, qty):
        self._photo = photologue.models.Photo.objects.get(pk=photo_id)
        self._quantity = qty
        self._size = s
        
    def get_photo(self):
        return self._photo
    photo = property(get_photo)
    
    def get_quantity(self):
        return self._quantity
    quantity = property(get_quantity)
    
    def get_size(self):
        return self._size
    size = property(get_size)
    
    def cost(self):
        return self.unit_cost() * self.quantity
    
    def unit_cost(self):
        if (self._size=='4x6'):
            return 0.2
        elif (self._size=='5x7'):
            return 0.5
        elif (self._size=='8x10'):
            return 1.5
        elif (self._size=='11x13'):
            return 8.0
        else:
            return 55.00
    
class OrderForm(forms.Form):
    photoId = forms.IntegerField(widget = forms.HiddenInput())
    p4x6 = forms.ChoiceField(
                    label='4x6 Print',
                    widget=forms.Select(attrs={'onchange':"update_print_prices('prod3')"}),
                    choices=
                    (('0','0'),
                     ('1','1'),
                     ('2','2'), 
                     ('3','3'),
                     ('4','4'),
                     ('5','5'), 
                     ('6','6'),)
                    )
    p5x7 = forms.ChoiceField(label='5x7 Print',
                    widget=forms.Select(attrs={'onchange':"update_print_prices('prod3')"}),
                    choices=
                    (('0','0'),
                     ('1','1'),
                     ('2','2'), 
                     ('3','3'),
                     ('4','4'),
                     ('5','5'), 
                     ('6','6'),)
                    )
    p8x10 = forms.ChoiceField(label='8x10 Print',
                    widget=forms.Select(attrs={'onchange':"update_print_prices('prod3')"}),
                    choices=
                    (('0','0'),
                     ('1','1'),
                     ('2','2'), 
                     ('3','3'),
                     ('4','4'),
                     ('5','5'), 
                     ('6','6'),)
                    ) 
    p11x13 = forms.ChoiceField(label='11x13 Print',
                    widget=forms.Select(attrs={'onchange':"update_print_prices('prod3')"}),
                    choices=
                    (('0','0'),
                     ('1','1'),
                     ('2','2'), 
                     ('3','3'),
                     ('4','4'),
                     ('5','5'), 
                     ('6','6'),)
                    )   
   
class Cart():
    items_array = []
    def items(self):
        return len(self.items_array);
    def add_item(self, item):
        if (item.quantity > 0):
            for a in self.items_array:
                if (a.photo.pk == item.photo.pk and a.size == item.size):
                    self.items_array.remove(a)
                    self.items_array.append(OrderItem(a.photo.pk, a.size, 
                                                      item.quantity))
                    return
            self.items_array.append(item)
    def checkout_items(self):
        return items_array        
    
def order(request):
    if request.method=="POST":
        order_form = OrderForm(request.POST)
        order_form.is_valid()
        cart = request.session.get('cart', Cart())
        photoId = int(order_form.cleaned_data['photoId'])
        cart.add_item(OrderItem(photoId,'4x6',int(order_form.cleaned_data['p4x6'])))
        cart.add_item(OrderItem(photoId,'5x7',int(order_form.cleaned_data['p5x7'])))
        cart.add_item(OrderItem(photoId,'8x10',int(order_form.cleaned_data['p8x10'])))
        cart.add_item(OrderItem(photoId,'11x13',int(order_form.cleaned_data['p11x13'])))
        request.session['cart'] = cart
    return HttpResponse('ok')

def add_movie(request):
    if (not request.FILES['movie'] or not request.FILES['poster_frame']):
        return HttpResponse('error')
    return HttpResponse('ok')
    
def photo   (request, image_slug):
    catalog = Catalog.objects.get(name="riley")
    try:
        curr_image = PhotoProxy.objects.get(title_slug=image_slug)        
    except: 
        return HttpResponseRedirect('/')
    try: 
        v = curr_image.video
        curr_image = v
    except:
        pass #things are ok, if its a video
    
    ctype = ContentType.objects.get_for_model(curr_image)
    h_item = HistoricalItem.objects.get(content_type__pk = ctype.id, object_id = curr_image.id)
    
    prev_image_list = []
    try : 
        prev_image = h_item.get_previous_by_shown_date()
        for i in range(7):
            prev_image_list.append(PhotoProxy.objects.get(pk=prev_image.content_object.id))
            prev_image = prev_image.get_previous_by_shown_date()  
    except Exception as inst:
        print inst
                        
    try: 
        next_image = PhotoProxy.objects.get(pk = h_item.get_next_by_shown_date().content_object.id)   
    except:
        next_image = None  
         
                                    
    class CommentForm(ModelForm):
        class Meta:
            exclude = ['photo'] 
            model = Comment
    
    if (request.method == "POST"):
        formset = CommentForm(request.POST, request.FILES)
        if (formset.is_valid()): 
            comment = formset.save(commit=False)            
            comment.photo = curr_image
            try:
                comment.save()
                
                return HttpResponseRedirect('/r/'+curr_image.title_slug)
            except:
                pass
    
    comment_form = CommentForm()
    order_form = OrderForm(initial={'photoId': curr_image.id})
    
    #Monthly archives
    monthlyArchive = []
    for d in HistoricalItem.objects.dates('shown_date', 'month'):
        monthlyArchive.append({
                               'date' : str(d.month) + ' ' + str(d.year), 
                               'image' : HistoricalItem.objects.filter(shown_date__month=d.month, shown_date__year=d.year)[0]
                               })
        
    t = loader.get_template('index.django')
     
    return HttpResponse(t.render(RequestContext(request, 
                                         {
                                          'curr_image' : curr_image, 
                                          'prev_image_list' : prev_image_list,
                                          'next_image' : next_image, 
                                          'comment_form' : CommentForm(),
                                          'comments' : curr_image.comment_set.all(), 
                                          'today_image' : curr_image, 
                                          'archive_info' : monthlyArchive
                                          })))
def archive(request, year, month):
    t = loader.get_template('archive.django')
    
    photos = HistoricalItem.objects.filter(shown_date__month=month, shown_date__year=year).all()  
    return HttpResponse(t.render(RequestContext(request, {
                                                          'photo_list' : photos
                                                          })))
    
def index(request):  
    catalog = Catalog.objects.get(name="riley")
    curr_image = catalog.curr_item()
    return HttpResponseRedirect('/r/'+curr_image.content_object.title_slug)
