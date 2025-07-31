from fallback import build_crew

def main():
    print('Welcome to google AI Agent System')
    user_input = input("Enter your prompt :")
    
    results = build_crew(user_input)
    
    return results

if __name__ == "__main__":
     output = main()
     print('Task Executed Sucessfully', output)