string = "https://www.google.com/search?sxsrf=AOaemvJ9rY1n0LhRXTT2EjHvibjp23va6g:1640384752915&q=python+remove+everything+after+3rd+slash&spell=1&sa=X&ved=2ahUKEwjp5vezvf30AhWySt8KHY6tD9gQBSgAegQIBRAx&biw=1920&bih=877&dpr=1"

string = string.split("/")
print(string)

list1 = ["one", "two", "three", "four", "five"]
print(list1)
del list1[3:]
print(list1)