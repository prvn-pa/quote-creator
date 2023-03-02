from PIL import Image, ImageDraw, ImageFont

fileObject = open("sample.txt", "r")
sentence = fileObject.read()

#variables for image size
x1 = 612
y1 = 612

#my quote
#sentence = "text here"

#choose a font
fnt = ImageFont.truetype('./fonts/Pavanam.ttf', 30)

img = Image.new('RGB', (x1, y1), color = (132, 255, 202))
d = ImageDraw.Draw(img)

#find the average size of the letter
sum = 0
for letter in sentence:
  sum += d.textsize(letter, font=fnt)[0]

average_length_of_letter = sum/len(sentence)

#find the number of letters to be put on each line
number_of_letters_for_each_line = (x1/1.618)/average_length_of_letter
incrementer = 0
fresh_sentence = ''

#add some line breaks
for letter in sentence:
  if(letter == '-'):
    fresh_sentence += '\n\n' + letter
  elif(incrementer < number_of_letters_for_each_line):
    fresh_sentence += letter
  else:
    if(letter == ' '):
      fresh_sentence += '\n'
      incrementer = 0
    else:
      fresh_sentence += letter
  incrementer+=1

print (fresh_sentence)

#render the text in the center of the box
dim = d.textsize(fresh_sentence, font=fnt)
x2 = dim[0]
y2 = dim[1]

qx = (x1/2 - x2/2)
qy = (y1/2-y2/2)

d.text((qx,qy), fresh_sentence ,align="center",  font=fnt, fill=(100,100,100))

img.save('quote.png')
