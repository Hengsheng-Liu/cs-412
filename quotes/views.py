from django.shortcuts import render

# Create your views here.
import random
person = "Jean-Jacques Rousseau"
bio = "born in 1712, Rousseau was one of the most influential \
    thinkers of the Enlightenment era, known for his contributions to political philosophy, education, \
        and literature. Born in Geneva, Switzerland, Rousseau’s works profoundly impacted the French Revolution and the development of modern political, economic, and educational thought."
creator = "Hengsheng Liu"
quotes = [
    "People who know little are usually great talkers, while men who know much say little",
    "I prefer liberty with danger than peace with slavery.",
    "Man is born free, and everywhere he is in chains. ",
    "The world of reality has its limits; the world of imagination is boundless.",
    "It is too difficult to think nobly when one thinks only of earning a living.",
    "Every person has a right to risk their own life for the preservation of it.",
    "Civilization is a hopeless race to discover remedies for the evils it produces.",
    "Every man having been born free and master of himself, no one else may under any pretext whatever subject him without his consent. To assert that the son of a slave is born a slave is to assert that he is not born a man.",
    "The strongest is never strong enough to be always the master, unless he transforms strength into right, and obedience into duty.",
    "The general will is always right, but the judgment which guides it is not always enlightened.",

]

images = [
    "quotes/img/rousseau1.jpg",
    "quotes/img/rousseau2.jpeg",
    "quotes/img/rousseau3.jpeg",
    "quotes/img/rousseau4.jpeg",
]

def quote(request):
    random_quote = random.choice(quotes)
    random_image = random.choice(images)
    context = {
        'quote': random_quote,
        'image': random_image,
    }
    return render(request, 'quotes/quote.html', context)

def show_all(request):
    context = {
        'quotes': quotes,
        'images': images,
    }
    return render(request, 'quotes/show_all.html', context)

def about(request):
    context = {
        'person': person,
        'bio': bio,
        'creator': creator,
    }
    return render(request, 'quotes/about.html', context)