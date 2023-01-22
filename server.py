from flask import Flask, json, request
import math
import collections
import logging
import sys
import datetime
import os

app = Flask(__name__)

if not os.path.exists('logs'):#creation of logs folder
    os.makedirs('logs')

request_count = 0
format = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s: %(message)s | request #%(request_count)s","%d-%m-%Y %H:%M:%S")

request_logger_name = 'request-logger'
request_logger = logging.getLogger(request_logger_name)
request_logger.propagate = True
request_logger.setLevel(logging.INFO)
request_file = logging.FileHandler('logs\\requests.log', mode='w')#creation of requests log file
request_file.setFormatter(format)
request_logger.addHandler(request_file)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(format)
request_logger.addHandler(handler)

stack_logger_name = 'stack-logger'
stack_logger = logging.getLogger(stack_logger_name)
stack_logger.propagate = True
stack_logger.setLevel(logging.INFO)
stack_file = logging.FileHandler('logs\\stack.log', mode='w')#creation of stack log file
stack_file.setFormatter(format)
stack_logger.addHandler(stack_file)

independent_logger_name = 'independent-logger'
Independent_logger = logging.getLogger(independent_logger_name)
Independent_logger.propagate = True
Independent_logger.setLevel(logging.DEBUG)
Independent_file = logging.FileHandler('logs\\independent.log', mode='w')#creation of independent log file
Independent_file.setFormatter(format)
Independent_logger.addHandler(Independent_file)


stack = collections.deque()

@app.route('/logs/level', methods = ['GET'])
def Get_Log_Level():
    global request_count
    request_count += 1
    flag = False
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/logs/level', 'GET'), extra={"request_count": request_count})
    begin = datetime.datetime.now()
    res = ""
    dic = request.args.to_dict()
    logger_name = dic['logger-name']
    if logger_name == stack_logger_name:
        res = stack_logger.level
    elif logger_name == request_logger_name:
        res = request_logger.level
    elif logger_name == independent_logger_name:
        res = Independent_logger.level
    else:
        answer = "Error! The logger name does not exist!"
        app_res = app.response_class(response = answer)
        flag = True

    if flag == False:
        app_res = app.response_class(response = logging.getLevelName(res))
    
    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count, ((end - begin).microseconds)//1000), extra={"request_count": request_count})
    return app_res

@app.route('/logs/level', methods = ['PUT'])
def Set_Log_Level():
    global request_count
    request_count+= 1
    flag = False
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/logs/level', 'PUT'), extra={"request_count": request_count})
    begin = datetime.datetime.now()
    dic = request.args.to_dict()
    logger_name = dic['logger-name']
    logger_level = dic['logger-level']
    logger_level = logger_level.upper()
    if logger_level in ["ERROR","INFO","DEBUG"]:
        if logger_name == stack_logger_name:
            stack_logger.setLevel(logger_level)
        elif logger_name == request_logger_name:
            request_logger.setLevel(logger_level)
        elif logger_name == independent_logger_name:
            Independent_logger.setLevel(logger_level)
        else:
            answer = "Error! The logger name does not exist!"
            app_res = app.response_class(response = answer)
            flag = True
    else:
        answer = "Error! The logger level does not match the options available!"
        app_res = app.response_class(response = answer)
        flag = True
    if flag == False:
        app_res = app.response_class(response = logger_level)
    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count, ((end - begin).microseconds)//1000), extra={"request_count": request_count})
    return app_res




@app.route('/independent/calculate', methods = ['POST'])
def calculate():
    global request_count
    request_count+= 1
    begin = datetime.datetime.now()
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/independent/calculate', 'POST'), extra={"request_count": request_count})
    dic = json.loads(request.data)
    argument = dic["arguments"]
    operation = dic["operation"]
    operation = operation.lower()
    answer = checkValid(argument, operation)
    
    if type(answer) == str:
        Independent_logger.error("Server encountered an error ! message: {}".format(answer), extra={"request_count": request_count})
        result = bad_res(answer)
    else:
        Independent_logger.info("Performing operation {}. Result is {}".format(operation, answer), extra={"request_count": request_count})
        Independent_logger.debug("Performing operation: {}({},{}) = {}".format(operation, argument[0], argument[1], answer), extra={"request_count": request_count})
        result = good_res(answer)
    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count,((end - begin).microseconds)//1000), extra={"request_count": request_count})
    return result

    

def checkValid(argument, operation):
    if len(argument) > 2:
        return "Error: Too many arguments to perform the operation " + operation
    elif len(argument) < 2:
        if len(argument) == 1 and (operation == "fact" or operation == "abs"):
            if operation == "Abs":
                return Abs(argument[0])
            else:
                return Fact(argument[0])

        return "Error: Not enough arguments to perform the operation " + operation
    else:
        if operation in ["plus", "minus","times","divide","pow"]:
           return calc(operation, argument[0], argument[1])
        else:
            return "Error: unknown operation: " + operation
            


def good_res(good):
    AnsJson = json.dumps({'result': good, 'error-message': ''})
    response = app.response_class(
        response = AnsJson,
        status = 200,
        mimetype = 'application/json')
    return response

def bad_res(bad):
    AnsJson = json.dumps({'result': '', 'error-message': bad})
    response = app.response_class(
        response = AnsJson,
        status = 409,
        mimetype = 'application/json')
    return response


@app.route('/stack/size', methods = ['GET'])
def size():
    global request_count
    request_count+= 1
    begin = datetime.datetime.now()
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/stack/size', 'GET'), extra={"request_count": request_count})
    stack_logger.info("Stack size is {}".format(len(stack)), extra={"request_count": request_count})
    answer = len(stack)
    result = good_res(answer)
    
    
    res = "Stack content (first == top): ["
    for i in reversed (range (len(stack))):
        res += str(stack[i])
        if i > 0:
            res+= ', '
    res += ']'

    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count, ((end - begin).microseconds)//1000), extra={"request_count": request_count})
    stack_logger.debug(res, extra={"request_count": request_count})
    return result


@app.route('/stack/arguments', methods = ['PUT'])
def AddArgument():
    global request_count
    request_count+= 1
    begin = datetime.datetime.now()
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/stack/arguments', 'PUT'), extra={"request_count": request_count})
    before_addition = len(stack)
    dic = json.loads(request.data)
    counter = 0
    argument = dic["arguments"]
    res = "Adding arguments: "
    for i in range (len(argument)):
        counter += 1
        stack.append(argument[i])
        res += str(argument[i])
        if i < len(argument) - 1:
            res+= ','
    res += " | Stack size before {} | stack size after {}".format(before_addition, len(stack))

    stack_logger.info("Adding total of {} argument(s) to the stack | Stack size: {}".format(counter, len(stack)), extra={"request_count": request_count})
    stack_logger.debug(res, extra={"request_count": request_count})
    
    result = good_res(len(stack))

    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count,((end - begin).microseconds)//1000), extra={"request_count": request_count})
    return result


@app.route('/stack/operate', methods = ['GET'])
def Operate():
    global request_count
    request_count+= 1
    begin = datetime.datetime.now()
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/stack/operate', 'GET'), extra={"request_count": request_count})

    dic = request.args.to_dict()
    operations = dic["operation"]
    operations = operations.lower()
    if operations not in ["plus", "minus", "divide", "times", "pow", "abs", "fact"]:
        answer = "Error: unknown operation: " + operations
        result = bad_res(answer)
    else:
        if operations in ["abs","fact"]:
            if len(stack) >= 1:
                top = stack[len(stack) - 1]
                if operations == "abs":
                    answer = Abs(stack.pop())
                else:
                    answer = Fact(stack.pop())
                stack_logger.info("Performing operation {}. Result is {} | stack size: {}".format(operations, answer, len(stack)), extra={"request_count": request_count})
                stack_logger.debug("Performing operation: {}({}) = {}".format(operations, top, answer), extra={"request_count": request_count})

                result = good_res(answer)
            else:
                answer = "Error: cannot implement operation {}. It requires 2 arguments and the stack has only {} arguments".format(operations, len(stack)) 
                result = bad_res(answer)
        else:
            if len(stack) < 2:
                answer = "Error: cannot implement operation {}. It requires 2 arguments and the stack has only {} arguments".format(operations, len(stack)) 
                result = bad_res(answer)
            else:
                top = stack[len(stack) - 1]
                second_top = stack[len(stack) - 2]
                answer = calc(operations, stack.pop(), stack.pop())
                stack_logger.info("Performing operation {}. Result is {} | stack size: {}".format(operations, answer, len(stack)), extra={"request_count": request_count})
                stack_logger.debug("Performing operation: {}({},{}) = {}".format(operations, top, second_top, answer), extra={"request_count": request_count})
                
                if type(answer) == str:
                    result = bad_res(answer)
                else:
                    result = good_res(answer)
    if type(answer) == str:
        stack_logger.error("Server encountered an error ! message: {}".format(answer), extra={"request_count": request_count})
    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count, ((end - begin).microseconds)//1000), extra={"request_count": request_count})
    return result


               
@app.route('/stack/arguments', methods = ['DELETE'])
def Delete_From_Stack():
    global request_count
    request_count+= 1
    begin = datetime.datetime.now()
    request_logger.info("Incoming request | #{} | resource: {} | HTTP Verb {}".format(request_count, '/stack/arguments', 'DELETE'), extra={"request_count": request_count})
    answer = ""#empty string
    dic = request.args.to_dict()
    string_to_delete = dic["count"]
    num_to_delete = int(string_to_delete)
    if len(stack) < num_to_delete:
        answer = "Error: cannot remove {} from the stack. It has only {} arguments".format(num_to_delete, len(stack))
        result = bad_res(answer)
    else:
        for i in range(num_to_delete):
            stack.pop()
        answer = len(stack)
        result =  good_res(answer)
        stack_logger.info("Removing total {} argument(s) from the stack | Stack size: {}".format(num_to_delete, len(stack)), extra={"request_count": request_count})
    if type(answer) == str:
        stack_logger.error("Server encountered an error ! message: {}".format(answer), extra={"request_count": request_count})
    end = datetime.datetime.now()
    request_logger.debug("request #{} duration: {}ms".format(request_count,((end - begin).microseconds)//1000), extra={"request_count": request_count})
    return result
    


def calc(operation, num1, num2):
    if operation == "plus":
        return Plus(num1, num2)
    elif operation == "minus":
        return Minus(num1, num2)
    elif operation == "times":
        return Times(num1, num2)
    elif operation == "divide":
        return Divide(num1, num2)
    elif operation == "pow":
        return Pow(num1, num2)


def Plus(x,y):
    return x+y

def Minus(x,y):
    return x-y

def Times(x,y):
    return x*y

def Divide(x,y):
    if y==0:
        return "Error while performing operation Divide: division by 0"
    return int(x/y)

def Pow(x,y):
    return pow(x,y)

def Abs(x):
    return abs(x)

def Fact(x):
    if x < 0:
        return bad_res("Error while performing operation Factorial: not supported for the negative number")
    return math.factorial(x)

if __name__ == "__main__":  
    app.run(port=9285)

#query = comes with the url and is written at the end of the url
#to get it out: request.args.to_dict()
#body = dictionary that come seperated (assuming it is json type)
#to get it out: dic = json.loads(request.data)