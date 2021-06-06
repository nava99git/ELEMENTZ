from time import sleep

def nextSquare():
    i = 0;
    # An Infinite loop to generate squares
    while True:
        print('nextSquare: %d' % (i))
        yield i
        sleep(5)
        i += 1  # Next execution resumes
                # from this point

# Driver code to test above generator
# function
for value in nextSquare():
    print('main: %d' % (value))
    if value > 100:
         break
    print(value)
