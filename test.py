import datetime

first = datetime.datetime(year=2022, month=3, day=1)
second = datetime.datetime(year=2022, month=3, day=2)

result = second - first

print(result.days)
print(type(result.days))
