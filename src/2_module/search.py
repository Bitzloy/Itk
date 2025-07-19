sorted_list = [1, 2, 3, 45, 356, 569, 600, 705, 923]



def search(number: int) -> bool:
    left = 0
    right = len(sorted_list)
    
    while left <= right:
        middle = (left + right) // 2
        
        if sorted_list[middle] == number:
            return True
        
        elif sorted_list[middle] < number:
            left = middle + 1
        
        else:
            right = middle - 1
            
    return False
           



print(search(3))



