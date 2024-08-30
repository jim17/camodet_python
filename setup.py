import setuptools
import camodet

# Open README to fill longdescription
with open("README.md", "r") as fh:
    long_description = fh.read()

print("Packages: ", setuptools.find_packages())

setuptools.setup(
     name="camodet",
     version=camodet.__version__,
     scripts=[] ,
     author="Miguel A. Borrego",
     author_email="jimjim17@gmail.com",
     description="CAmera MOtion DETection application written in python language",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/jim17/camodet_python",
     packages=setuptools.find_packages(),
     install_requires=[
         "opencv-python==4.8.1.78",
         "numpy==1.18.1",
     ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
         "Operating System :: OS Independent",
     ],
)