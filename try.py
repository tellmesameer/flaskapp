print("Welcome to the Love Calculator!")

name1 = input("Enter your name: ").lower()

name2 = input("Enter the name of the person you love: ").lower()




combined_name = name1 + name2




true_count = 0

love_count = 0




true_count += combined_name.count('t')

true_count += combined_name.count('r')

true_count += combined_name.count('u')

true_count += combined_name.count('e')




love_count += combined_name.count('l')

love_count += combined_name.count('o')

love_count += combined_name.count('v')

love_count += combined_name.count('e')




score = int(str(true_count) + str(love_count))




if score < 10 or score > 90:

    message = "Your score is {}, you go together like coke and mentos.".format(score)

elif score >= 40 and score <= 50:

    message = "Your score is {}, you are alright together.".format(score)

else:

    message = "Your score is {}.".format(score)




print(message)