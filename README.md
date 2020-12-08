# ASCII-Generator.site

**This is a Django website for generating ASCII-arts out of images or text 🎨**

You can find it at [https://ASCII-Generator.site](https://ascii-generator.site)

> ![demo GIF](.github/media/demo.gif)</br>
> Demo (a bit old for now)

## Fast local setup

You can set up this project on your local network by using these easy steps:

- Clone this repo on your pc;
- Create virtual environment with ```virtualenv venv```, activate it and install dependencies with ```pip install -r requirements.txt```;
- At the top of ```project/settings.py``` set ```EASY_RUN_MODE``` from ```False``` to ```True```;
- Run ```python manage.py makemigrations``` and ```python manage.py migrate```;
- Start server by ```python manage.py runserver``` or ```python manage.py runserver 0.0.0.0:7777``` to open it to local network (for example, over wifi).

It will run faster locally than on actual website because of multi-threading (website is on virtual single-core cpu), file uploading time and actual distance to the server (ping).

## Used repositories

For creating this project, several open-source repositories were used:

#### Generators

- [ASCII-generator](https://github.com/uvipen/ASCII-generator) by [uvipen](https://github.com/uvipen) ([MIT-License - Copyright (c) 2018 Viet Nguyen](https://github.com/uvipen/ASCII-generator/blob/master/LICENSE));
- [asciify](https://github.com/RameshAditya/asciify) by [RameshAditya](https://github.com/RameshAditya);
- [art](https://github.com/sepandhaghighi/art) by [sepandhaghighi](https://github.com/sepandhaghighi) ([MIT-License - Copyright (c) 2017 Sepand Haghighi](https://github.com/sepandhaghighi/art/blob/master/LICENSE)).<br>Also, check out [his project's website](https://www.4r7.ir/).

#### Django apps

- [django-cleanup](https://github.com/un1t/django-cleanup) by [un1t](https://github.com/un1t) ([MIT-License - Copyright (C) 2012 by Ilya Shalyapin](https://github.com/un1t/django-cleanup/blob/master/LICENSE));
- [django-recaptcha](https://github.com/praekelt/django-recaptcha) by [praekelt](https://github.com/praekelt) ([BSD-3-Clause License - Copyright (c) Praekelt Consulting](https://github.com/praekelt/django-recaptcha/blob/develop/LICENSE));
- [django-rosetta](https://github.com/mbi/django-rosetta) by [mbi](https://github.com/mbi) ([MIT-License - Copyright (c) 2008-2010 Marco Bonetti](https://github.com/mbi/django-rosetta/blob/develop/LICENSE)).

## Personal Todo
- [x] ~~Add support for more image file types;~~
- [x] ~~Implement languages;~~
- [x] ~~Option to share generated results with access by link;~~
- [ ] Integrate neural-network-based image to ASCII art generator;
- [ ] Video to ASCII.

## Other

[Contributing](CONTRIBUTING.md).

[License](LICENSE).

Icons made by [Freepik](https://www.flaticon.com/authors/freepik) and [Pixel Perfect](https://www.flaticon.com/authors/pixel-perfect) from [www.flaticon.com](https://www.flaticon.com/).
