imgPath = 'https://i.dailymail.co.uk/i/pix/2017/09/05/13/43EDB60400000578-4853956-A_four_bedroom_family_home_on_Australia_s_most_famous_street_has-a-3_1504613460264.jpg'
size(512, 512)
scale(1.4)
translate(-99, -21)
image(imgPath, (0, 0))
import os
saveImage(os.path.join(os.getcwd(), 'RamsayStMechanicIcon.png'))
