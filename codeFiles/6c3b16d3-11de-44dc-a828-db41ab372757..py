testcase = int(input())
while testcase >0 :
    input_string = input()
    numbers = input_string.split()
    numbers = [int(num) for num in numbers]
    sum = sum(numbers)
    print(sum)
    testcase -= 1