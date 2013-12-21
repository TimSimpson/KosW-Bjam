#include <iostream>
#include <string>
#include <sstream>


using namespace std;


int main(int argc, char ** argv)
{
    if (argc < 1)
    {
        cout << "Expected argument zero.";
        return 1;
    }
    string exeName = argv[0];
    if (string::npos != exeName.find(".exe", exeName.size() - 4))
    {
        exeName = exeName.substr(0, exeName.size() - 4);
    }
    stringstream ss;
    ss << "python " << exeName << ".py ";
    for (int i = 1; i < argc; i ++)
    {
        ss << " " << argv[i];
    }
    string args(ss.str());
    return system(args.c_str());
}
