# ASCII-Generator.site

**This is a Django website for generating ASCII-arts out of images or text 🎨**

You can find it at [https://ASCII-Generator.site](https://ascii-generator.site)

> ![demo GIF](.github/media/demo.gif)</br>
> Demo (a bit old for now)

## Fast local setup

You start this website locally by using these easy steps (python3 is needed):

- Clone this repo to your pc;
- Create virtual environment (if needed) with ```virtualenv venv```, activate it and install dependencies with ```pip install -r requirements.txt```;
- At the top of ```project/settings.py``` set ```EASY_RUN_MODE``` from ```False``` to ```True```;
- Start server with```python manage.py runserver``` or ```python manage.py runserver 0.0.0.0:1234``` to open it to local network (for example, over wifi).

TAKE A NOTE that without postgresql, you can't use any database-related actions, only the generators.

## Used repositories

For creating this project, several open-source repositories were used:

#### Generators

- [ASCII-generator](https://github.com/uvipen/ASCII-generator) by [uvipen](https://github.com/uvipen) ([MIT-License - Copyright (c) 2018 Viet Nguyen](https://github.com/uvipen/ASCII-generator/blob/master/LICENSE));
- [asciify](https://github.com/RameshAditya/asciify) by [RameshAditya](https://github.com/RameshAditya);
- [art](https://github.com/sepandhaghighi/art) by [sepandhaghighi](https://github.com/sepandhaghighi) ([MIT-License - Copyright (c) 2017 Sepand Haghighi](https://github.com/sepandhaghighi/art/blob/master/LICENSE)).<br>You can visit [his project's website](https://www.4r7.ir/).

## Other

[Contributing](CONTRIBUTING.md).

[License](LICENSE).

Icons made by [Freepik](https://www.flaticon.com/authors/freepik) and [Pixel Perfect](https://www.flaticon.com/authors/pixel-perfect) from [www.flaticon.com](https://www.flaticon.com/).
